"""
录音回顾路由

录音上传、转写、总结
"""
import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi.responses import StreamingResponse
import logging

from app.database import get_db
from app.models.user import User
from app.models.review import ReviewRecord, Transcription, Summary
from app.schemas.review import (
    ReviewRecordResponse,
    ReviewUploadResponse,
    ReviewDetailResponse,
    TranscriptionResponse,
    SummaryResponse,
)
from app.services.asr_service import asr_service
from app.services.xinghuo_service import xinghuo_service
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException
from app.config import settings

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/review", tags=["录音回顾"])


# ============ 音频上传 ============

@router.post("/upload", response_model=ReviewUploadResponse)
@handle_app_errors
async def upload_audio(
    audio: UploadFile = File(..., description="音频文件"),
    record_type: str = Form(..., description="课程/会议"),
    language: str = Form(default="mandarin", description="语言"),
    title: Optional[str] = Form(default=None, description="标题"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传音频文件

    1. 验证音频格式和大小
    2. 保存音频文件到存储
    3. 创建录音记录（状态：pending）
    4. 异步触发ASR转写
    5. 异步触发AI总结
    """
    logger.info(f"[Review] Upload audio request - user: {current_user.id}, type: {record_type}, lang: {language}")

    # 验证文件类型
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/m4a", "audio/mp4"]
    if audio.content_type not in allowed_types:
        raise ValidationException(
            message="不支持的音频格式",
            details={"allowed_types": ["mp3", "wav", "m4a"], "received": audio.content_type}
        )

    # 验证文件大小 (50MB = 50 * 1024 * 1024)
    max_size = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
    content = await audio.read()
    if len(content) > max_size:
        raise ValidationException(
            message=f"音频文件过大，最大支持 {settings.MAX_AUDIO_SIZE_MB}MB",
            details={"max_size_mb": settings.MAX_AUDIO_SIZE_MB, "file_size_mb": len(content) / 1024 / 1024}
        )

    # 保存音频文件
    audio_dir = Path(settings.UPLOAD_DIR) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(audio.filename).suffix or ".mp3"
    file_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = audio_dir / file_name

    with open(file_path, "wb") as f:
        f.write(content)

    audio_url = f"/uploads/audio/{file_name}"
    logger.info(f"[Review] Audio saved to: {file_path}, url: {audio_url}")

    # 创建录音记录
    record = ReviewRecord(
        user_id=current_user.id,
        record_type=record_type,
        title=title or f"{record_type}录音",
        audio_url=audio_url,
        language=language,
        status="processing"  # 立即设置为processing
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    logger.info(f"[Review] Review record created: id={record.id}, status=processing")

    # 异步触发转写和总结
    asyncio.create_task(process_review_async(record.id, str(file_path), language, db))

    return ReviewUploadResponse(
        success=True,
        record_id=record.id,
        message="音频上传成功，正在转写中...",
        status="processing"
    )


async def process_review_async(record_id: int, audio_path: str, language: str, db: AsyncSession):
    """
    异步处理录音转写和总结

    1. 调用ASR服务转写
    2. 保存转写结果
    3. 调用星火大模型生成总结
    4. 保存总结结果
    5. 更新记录状态
    """
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            logger.info(f"[Review] Starting async processing for record: {record_id}")

            # 更新状态为处理中
            result = await session.execute(
                select(ReviewRecord).where(ReviewRecord.id == record_id)
            )
            record = result.scalar_one_or_none()
            if not record:
                logger.error(f"[Review] Record not found: {record_id}")
                return

            # ============ ASR转写 ============
            logger.info(f"[Review] Calling ASR service for record: {record_id}")
            try:
                asr_result = await asr_service.recognize_file(audio_path, language)
                raw_text = asr_result.get("text", "")
                segments = asr_result.get("segments", [])
                duration_ms = asr_result.get("duration_ms", 0)

                # 更新录音时长
                record.duration = duration_ms // 1000  # 转换为秒

                # 保存转写结果
                transcription = Transcription(
                    record_id=record_id,
                    raw_text=raw_text,
                    segments=segments
                )
                session.add(transcription)
                logger.info(f"[Review] Transcription completed for record: {record_id}, text length: {len(raw_text)}, duration: {record.duration}s")
            except Exception as e:
                logger.error(f"[Review] Transcription failed for record: {record_id}: {e}")
                # 转写失败，更新记录状态
                record.status = "failed"
                await session.commit()
                return

            # ============ AI总结 ============
            logger.info(f"[Review] Calling AI summary for record: {record_id}")
            try:
                logger.info(f"[Review] AI summary input - raw_text length: {len(raw_text)}, record_type: {record.record_type}")
                summary_result = await generate_summary_async(raw_text, record_type=record.record_type, user_id=str(record.user_id))
                logger.info(f"[Review] AI summary raw result keys: {list(summary_result.keys()) if isinstance(summary_result, dict) else 'not a dict'}")

                # 将列表转换为字符串（AI可能返回列表格式）
                def to_string(val):
                    if val is None:
                        return None
                    if isinstance(val, list):
                        return "\n".join(str(v) for v in val)
                    return str(val)

                # 根据记录类型保存对应的字段
                if record.record_type == "meeting":
                    # 会议类型使用会议专用字段
                    summary = Summary(
                        record_id=record_id,
                        topic=to_string(summary_result.get("topic")),
                        key_points=to_string(summary_result.get("discussion_points")),  # 讨论要点
                        difficulties=to_string(summary_result.get("resolutions")),     # 决议事项
                        memorable_quote=to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None,
                        next_suggestion=to_string(summary_result.get("action_items")),  # 行动项
                        discussion_points=to_string(summary_result.get("discussion_points")),
                        resolutions=to_string(summary_result.get("resolutions")),
                        action_items=to_string(summary_result.get("action_items")),
                        full_text=to_string(summary_result.get("full_text"))
                    )
                else:
                    # 课程类型使用课程专用字段
                    summary = Summary(
                        record_id=record_id,
                        topic=to_string(summary_result.get("topic")),
                        key_points=to_string(summary_result.get("key_points")),
                        difficulties=to_string(summary_result.get("difficulties")),
                        memorable_quote=to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None,
                        next_suggestion=to_string(summary_result.get("next_suggestion")),
                        full_text=to_string(summary_result.get("full_text"))
                    )
                session.add(summary)
                logger.info(f"[Review] Summary completed for record: {record_id}, type: {record.record_type}")
            except Exception as e:
                # 使用 %s 格式化避免 f-string 中的花括号问题
                logger.error(f"[Review] Summary failed for record: {record_id}, error type: %s, error: %s", type(e).__name__, str(e))
                import traceback
                logger.error(f"[Review] Traceback: {traceback.format_exc()}")
                # 总结失败，继续流程
                summary = None

            # 更新记录状态为完成
            record.status = "completed"
            await session.commit()
            logger.info(f"[Review] Processing completed for record: {record_id}")

        except Exception as e:
            logger.error(f"[Review] Async processing failed for record: {record_id}: {e}", exc_info=True)
            try:
                result = await session.execute(
                    select(ReviewRecord).where(ReviewRecord.id == record_id)
                )
                record = result.scalar_one_or_none()
                if record:
                    record.status = "failed"
                    await session.commit()
            except Exception as inner_e:
                logger.error(f"[Review] Failed to update record status: {inner_e}")


def _clean_code_syntax(text: str) -> str:
    """清理代码格式，转换为纯文本"""
    import re
    if not text:
        return text

    # 处理 {'key': 'value'} 或 {"key": "value"} 格式
    # 匹配并提取内容
    def replace_dict(match):
        content = match.group(0)
        # 提取所有 key: value 对
        pairs = re.findall(r"['\"]?(\w+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", content)
        if pairs:
            return " | ".join([f"{k}: {v}" for k, v in pairs])
        return content

    # 清理所有 {...} 格式的代码
    text = re.sub(r'\{[^{}]*\}', replace_dict, text)

    # 移除残留的单引号
    text = text.replace("'", "")

    # 清理多余的空格和换行
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def _is_template_content(text: str) -> bool:
    """检测是否为模板占位符内容"""
    import re
    if not text:
        return True
    # 检测是否包含模板特征词（这些是prompt中的说明，不是真正的分析内容）
    template_phrases = [
        "详细描述讨论了什么问题",
        "各方观点",
        "最终结论是什么",
        "决定的具体内容",
        "任务内容说明",
        "负责人：XXX",
        "截止时间：XXX",
        "根据转写内容分析",
        "根据转写内容总结",
        "根据转写内容",
    ]
    text_lower = text.lower()
    match_count = sum(1 for phrase in template_phrases if phrase.lower() in text_lower)
    # 如果匹配多个模板短语，认为是模板内容
    return match_count >= 2

def _parse_list_field(value) -> list:
    """解析列表字段，支持多种格式"""
    import re
    if isinstance(value, list):
        result = []
        for item in value:
            cleaned = _clean_code_syntax(str(item))
            # 如果清理后还有代码格式，进一步处理
            if re.search(r'\{[^}]+\}', cleaned):
                cleaned = re.sub(r'\{[^}]+\}', '', cleaned)
            cleaned = cleaned.strip()
            # 过滤掉模板内容
            if cleaned and not _is_template_content(cleaned) and len(cleaned) > 10:
                result.append(cleaned)
        return result if result else ["内容整理中，请稍后刷新查看"]
    elif isinstance(value, str):
        # 清理代码格式
        cleaned = _clean_code_syntax(value)

        # 按换行符分割
        items = [item.strip() for item in cleaned.split('\n') if item.strip()]

        # 如果只有一个元素且包含多个分隔内容，按 | 或 ; 分割
        if len(items) == 1 and items[0]:
            # 进一步清理可能的残留格式
            single = items[0]
            if re.search(r'\{[^}]+\}', single):
                # 提取 {...} 内的内容
                single = re.sub(r'\{[^}]+\}', lambda m: m.group(0)[1:-1], single)

            # 按 | 或 ; 分割
            sub_items = re.split(r'[|;]', single)
            if len(sub_items) > 1:
                items = [s.strip() for s in sub_items if s.strip() and len(s.strip()) > 10]

        # 过滤掉模板内容
        filtered_items = [item for item in items if not _is_template_content(item) and len(item) > 10]
        return filtered_items if filtered_items else [cleaned] if cleaned else ["内容整理中，请稍后刷新查看"]
    else:
        return [str(value)] if value else []


async def generate_summary_async(raw_text: str, record_type: str = "course", user_id: str = "0") -> dict:
    """
    调用星火大模型生成总结

    Args:
        raw_text: 原始转写文本
        record_type: 录音类型（course/meeting）
        user_id: 用户ID

    Returns:
        总结结果字典
    """
    import re

    if record_type == "course":
        prompt = f"""请对以下课程录音进行深度总结，生成一份丰富、结构化的课程笔记。

转写内容：
{raw_text[:10000]}

【关键要求】你必须返回标准的JSON对象格式，不能返回任何其他格式。不要返回 Markdown、纯文本或其他格式，只能返回JSON。

请严格按以下JSON格式返回（必须是可以被json.loads解析的格式）：
{{
    "topic": "课程主题（一句话概括，不超过20个字）",
    "key_points": [
        "第一，知识点1的详细描述（至少50字）",
        "第二，知识点2的详细描述（至少50字）",
        "第三，知识点3的详细描述（至少50字）"
    ],
    "difficulties": [
        "重点1的描述及解决方法",
        "难点2的描述及解决方法"
    ],
    "memorable_quote": "金句摘录（50字以内）",
    "next_suggestion": "预习建议（100字以内）",
    "full_text": "完整课程总结（300-500字）"
}}

【重要】严格禁止以下输出格式：
- 禁止输出非JSON格式，必须是纯JSON对象
- 禁止输出 Markdown 代码块（如 ```json ... ```）
- 禁止输出纯文本或其他格式
- 只返回JSON对象，不要有任何其他文字

错误示例（禁止）：
```json
{{...}}
```
或
这是一段课程总结...

正确示例（必须）：
{{"topic": "...", "key_points": [...], ...}}
"""
    else:  # meeting
        prompt = f"""请对以下会议录音进行深度总结，生成一份专业的会议纪要。

转写内容：
{raw_text[:10000]}

【关键要求】
1. 你必须返回标准的JSON对象格式，只能返回JSON
2. 输出的内容必须基于上述转写内容分析得出，不能是模板或占位符
3. 如果转写内容较少或不够详细，discussion_points可以只输出1-2条，但每条内容至少50字
4. 绝对禁止直接输出类似"议题一：详细描述讨论了什么问题"这样的模板文字

请严格按以下JSON格式返回：
{{
    "topic": "会议主题（一句话概括，不超过20个字）",
    "discussion_points": [
        "根据转写内容分析：会议讨论了XXX问题，各方观点是XXX，最终结论是XXX（至少50字）",
        "根据转写内容分析：会议讨论了XXX问题，各方观点是XXX，最终结论是XXX（至少50字）"
    ],
    "resolutions": [
        "根据转写内容总结的具体决议1",
        "根据转写内容总结的具体决议2"
    ],
    "action_items": [
        "具体待办任务1，负责人：XXX",
        "具体待办任务2，负责人：XXX"
    ],
    "memorable_quote": "转写中出现的最重要或最有趣的一句话（50字以内）",
    "full_text": "完整会议总结（300-500字），必须包含会议的主要讨论内容和结果"
}}

正确示例：
{{"topic": "项目进度评审会议", "discussion_points": ["会议讨论了当前项目进度滞后的原因，主要是因为需求变更频繁导致开发周期延长，各方同意优化需求变更流程", "会议确定了下一阶段的技术方案选择，经过比较决定采用微服务架构"], "resolutions": ["决定本周五前完成技术方案文档", "决定下周开始用户调研"], "action_items": ["张三负责整理技术方案文档，截止周五", "李四负责安排用户调研时间"], "memorable_quote": "产品质量是我们最核心的竞争力", "full_text": "本次会议主要围绕..."}}"""

    messages = [{"role": "user", "content": prompt}]
    result = await xinghuo_service.chat_completion(messages, user_id=user_id)

    # 记录原始返回结果（前1000字符）
    logger.info(f"[Review] AI response length: {len(result)}, preview: {result[:200]}")

    # 解析JSON结果
    import json
    try:
        # 尝试提取JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        else:
            # 尝试找到JSON对象
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                result = json_match.group()

        logger.info(f"[Review] Parsed JSON, result length: {len(result)}")

        summary_data = json.loads(result.strip())

        # 清理列表字段中的代码格式
        if record_type == "course":
            summary_data["key_points"] = _parse_list_field(summary_data.get("key_points", []))
            summary_data["difficulties"] = _parse_list_field(summary_data.get("difficulties", []))
        else:
            summary_data["discussion_points"] = _parse_list_field(summary_data.get("discussion_points", []))
            summary_data["resolutions"] = _parse_list_field(summary_data.get("resolutions", []))
            summary_data["action_items"] = _parse_list_field(summary_data.get("action_items", []))

        logger.info(f"[Review] Summary parsed successfully")
        return summary_data
    except json.JSONDecodeError as e:
        # JSON解析失败，尝试从非JSON格式中提取信息
        logger.warning("[Review] JSON parse failed, trying fallback extraction: %s", str(e)[:100])
        fallback_result = _extract_from_text(result, record_type, raw_text)
        if fallback_result:
            logger.info("[Review] Fallback extraction successful")
            return fallback_result

        # 使用 %s 避免 f-string 中的花括号问题
        logger.error("[Review] Fallback extraction also failed, using basic fallback")
        return {
            "topic": "总结生成",
            "key_points": _parse_list_field(["内容整理中，请稍后刷新查看"]) if record_type == "course" else [],
            "difficulties": [],
            "memorable_quote": "",
            "next_suggestion": "",
            "full_text": raw_text[:1000] if raw_text else ""
        }


def _extract_from_text(text: str, record_type: str, raw_text: str) -> dict:
    """从非JSON格式的文本中提取摘要信息"""
    import re

    result = {
        "topic": "总结生成",
        "key_points": [],
        "difficulties": [],
        "memorable_quote": "",
        "next_suggestion": "",
        "full_text": ""
    }

    if not text:
        return None

    # 尝试提取topic
    topic_match = re.search(r'[一二三四五六七八九十]+[\\.、:：]\s*.*?主题[^\\n]*",?([^\\n]+)', text)
    if topic_match:
        result["topic"] = topic_match.group(1).strip()
    else:
        # 尝试其他模式
        topic_match = re.search(r'主题[：:]?\s*([^\\n,，]+)', text)
        if topic_match:
            result["topic"] = topic_match.group(1).strip()[:20]

    # 尝试提取会议内容
    if record_type == "meeting":
        discussion_points = []
        resolutions = []
        action_items = []

        # 按行分割，提取讨论要点
        lines = text.split('\n')
        current_section = None
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # 识别章节
            if any(kw in line for kw in ['议题', '讨论', '内容', '策划', '审核']):
                current_section = 'discussion'
                if len(line) > 10:
                    discussion_points.append(line)
            elif any(kw in line for kw in ['决议', '决定', '确定']):
                current_section = 'resolution'
                if len(line) > 10:
                    resolutions.append(line)
            elif any(kw in line for kw in ['待办', '行动', '任务', '负责人']):
                current_section = 'action'
                if len(line) > 10:
                    action_items.append(line)
            elif current_section and len(line) > 10:
                if current_section == 'discussion':
                    discussion_points.append(line)
                elif current_section == 'resolution':
                    resolutions.append(line)
                elif current_section == 'action':
                    action_items.append(line)

        # 清理并限制长度
        result["discussion_points"] = [dp[:200] for dp in discussion_points[:5] if len(dp) > 10]
        result["resolutions"] = [r[:200] for r in resolutions[:5] if len(r) > 10]
        result["action_items"] = [a[:200] for a in action_items[:5] if len(a) > 10]

        if result["discussion_points"] or result["resolutions"] or result["action_items"]:
            result["full_text"] = raw_text[:500] if raw_text else ""
            return result

    # 尝试提取课程内容
    elif record_type == "course":
        key_points = []

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.startswith('#') and not line.startswith('```'):
                key_points.append(line)

        result["key_points"] = [kp[:200] for kp in key_points[:5] if len(kp) > 20]

        if result["key_points"]:
            result["full_text"] = raw_text[:500] if raw_text else ""
            return result

    return None


# ============ 获取录音列表 ============

@router.get("", response_model=List[ReviewRecordResponse])
@handle_app_errors
async def get_review_records(
    status: Optional[str] = None,
    record_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的录音回顾列表

    Args:
        status: 可选的状态过滤（pending/processing/completed/failed）
        record_type: 可选的类型过滤（course/meeting）
        skip: 跳过数量（分页）
        limit: 返回数量（默认20）
    """
    logger.info(f"[Review] Get review records - user: {current_user.id}, status: {status}, type: {record_type}")

    query = select(ReviewRecord).where(
        and_(
            ReviewRecord.user_id == current_user.id,
            ReviewRecord.is_deleted == False
        )
    )

    if status:
        query = query.where(ReviewRecord.status == status)
    if record_type:
        query = query.where(ReviewRecord.record_type == record_type)

    query = query.order_by(ReviewRecord.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    records = result.scalars().all()

    logger.info(f"[Review] Found {len(records)} review records")
    return [ReviewRecordResponse.model_validate(r) for r in records]


# ============ 获取录音详情 ============

@router.get("/{record_id}", response_model=ReviewDetailResponse)
@handle_app_errors
async def get_review_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取录音回顾详情

    包含录音信息、转写结果、总结结果
    """
    logger.info(f"[Review] Get review detail - record_id: {record_id}, user: {current_user.id}")

    # 查询记录
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    # 查询转写结果
    transcription_result = await db.execute(
        select(Transcription).where(Transcription.record_id == record_id)
    )
    transcription = transcription_result.scalar_one_or_none()

    # 查询总结结果
    summary_result = await db.execute(
        select(Summary).where(Summary.record_id == record_id)
    )
    summary = summary_result.scalar_one_or_none()

    logger.info(f"[Review] Review detail retrieved - record_id: {record_id}, has_transcription: {transcription is not None}, has_summary: {summary is not None}")

    return ReviewDetailResponse(
        id=record.id,
        record_type=record.record_type,
        title=record.title,
        audio_url=record.audio_url,
        duration=record.duration,
        language=record.language,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        transcription=TranscriptionResponse.model_validate(transcription) if transcription else None,
        summary=SummaryResponse.model_validate(summary) if summary else None
    )


# ============ 重新生成AI摘要 ============

@router.post("/{record_id}/regenerate-summary")
@handle_app_errors
async def regenerate_summary(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    重新生成指定录音的AI摘要

    1. 验证记录存在且属于当前用户
    2. 获取转写文本
    3. 调用星火大模型生成新的摘要
    4. 更新或创建摘要记录
    """
    logger.info(f"[Review] Regenerate summary request - record_id: {record_id}, user: {current_user.id}")

    # 验证记录存在且属于当前用户
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    # 获取转写结果
    transcription_result = await db.execute(
        select(Transcription).where(Transcription.record_id == record_id)
    )
    transcription = transcription_result.scalar_one_or_none()

    if not transcription or not transcription.raw_text:
        raise ValidationException(message="转写文本不存在，无法重新生成摘要")

    raw_text = transcription.raw_text
    logger.info(f"[Review] Regenerating summary for record: {record_id}, text length: {len(raw_text)}, type: {record.record_type}")

    try:
        # 调用AI生成摘要
        summary_result = await generate_summary_async(
            raw_text,
            record_type=record.record_type,
            user_id=str(record.user_id)
        )

        # 将列表转换为字符串
        def to_string(val):
            if val is None:
                return None
            if isinstance(val, list):
                return "\n".join(str(v) for v in val)
            return str(val)

        # 检查是否已存在摘要
        existing_summary_result = await db.execute(
            select(Summary).where(Summary.record_id == record_id)
        )
        existing_summary = existing_summary_result.scalar_one_or_none()

        if existing_summary:
            # 更新现有摘要
            if record.record_type == "meeting":
                existing_summary.topic = to_string(summary_result.get("topic"))
                existing_summary.key_points = to_string(summary_result.get("discussion_points"))
                existing_summary.difficulties = to_string(summary_result.get("resolutions"))
                existing_summary.memorable_quote = to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None
                existing_summary.next_suggestion = to_string(summary_result.get("action_items"))
                existing_summary.discussion_points = to_string(summary_result.get("discussion_points"))
                existing_summary.resolutions = to_string(summary_result.get("resolutions"))
                existing_summary.action_items = to_string(summary_result.get("action_items"))
                existing_summary.full_text = to_string(summary_result.get("full_text"))
            else:
                existing_summary.topic = to_string(summary_result.get("topic"))
                existing_summary.key_points = to_string(summary_result.get("key_points"))
                existing_summary.difficulties = to_string(summary_result.get("difficulties"))
                existing_summary.memorable_quote = to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None
                existing_summary.next_suggestion = to_string(summary_result.get("next_suggestion"))
                existing_summary.full_text = to_string(summary_result.get("full_text"))
            summary = existing_summary
            logger.info(f"[Review] Updated existing summary for record: {record_id}")
        else:
            # 创建新摘要
            if record.record_type == "meeting":
                summary = Summary(
                    record_id=record_id,
                    topic=to_string(summary_result.get("topic")),
                    key_points=to_string(summary_result.get("discussion_points")),
                    difficulties=to_string(summary_result.get("resolutions")),
                    memorable_quote=to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None,
                    next_suggestion=to_string(summary_result.get("action_items")),
                    discussion_points=to_string(summary_result.get("discussion_points")),
                    resolutions=to_string(summary_result.get("resolutions")),
                    action_items=to_string(summary_result.get("action_items")),
                    full_text=to_string(summary_result.get("full_text"))
                )
            else:
                summary = Summary(
                    record_id=record_id,
                    topic=to_string(summary_result.get("topic")),
                    key_points=to_string(summary_result.get("key_points")),
                    difficulties=to_string(summary_result.get("difficulties")),
                    memorable_quote=to_string(summary_result.get("memorable_quote"))[:500] if summary_result.get("memorable_quote") else None,
                    next_suggestion=to_string(summary_result.get("next_suggestion")),
                    full_text=to_string(summary_result.get("full_text"))
                )
            db.add(summary)
            logger.info(f"[Review] Created new summary for record: {record_id}")

        await db.commit()
        await db.refresh(summary)

        return {
            "success": True,
            "message": "摘要重新生成成功",
            "summary_id": summary.id
        }

    except Exception as e:
        logger.error(f"[Review] Regenerate summary failed for record: {record_id}: {str(e)}", exc_info=True)
        await db.rollback()
        raise


# ============ 更新录音记录 ============

@router.put("/{record_id}", response_model=ReviewRecordResponse)
@handle_app_errors
async def update_review_record(
    record_id: int,
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新录音记录
    """
    logger.info(f"[Review] Update review record: {record_id}")

    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    if title is not None:
        record.title = title

    await db.commit()
    await db.refresh(record)

    return ReviewRecordResponse.model_validate(record)


# ============ 删除录音记录 ============

@router.delete("/{record_id}")
@handle_app_errors
async def delete_review_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除录音记录（软删除）
    """
    logger.info(f"[Review] Delete review record: {record_id}")

    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    # 软删除
    record.is_deleted = True
    await db.commit()

    return {"success": True, "message": "删除成功"}


# ============ 获取转写结果 ============

@router.get("/{record_id}/transcription", response_model=Optional[TranscriptionResponse])
@handle_app_errors
async def get_transcription(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定记录的转写结果
    """
    logger.info(f"[Review] Get transcription: {record_id}")

    # 验证记录存在且属于当前用户
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    # 查询转写结果
    transcription_result = await db.execute(
        select(Transcription).where(Transcription.record_id == record_id)
    )
    transcription = transcription_result.scalar_one_or_none()

    if not transcription:
        return None

    return TranscriptionResponse.model_validate(transcription)


# ============ 获取总结结果 ============

@router.get("/{record_id}/summary", response_model=Optional[SummaryResponse])
@handle_app_errors
async def get_summary(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定记录的总结结果
    """
    logger.info(f"[Review] Get summary: {record_id}")

    # 验证记录存在且属于当前用户
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundException("ReviewRecord", record_id)

    # 查询总结结果
    summary_result = await db.execute(
        select(Summary).where(Summary.record_id == record_id)
    )
    summary = summary_result.scalar_one_or_none()

    if not summary:
        return None

    return SummaryResponse.model_validate(summary)