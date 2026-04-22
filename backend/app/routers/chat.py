"""
聊天路由

AI对话、消息历史、会话管理
"""
import os
import time
import uuid
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, StudentProfile
from app.models.chat import Conversation, Message
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageResponse,
    VoiceResponse
)
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException, ThirdPartyException
from app.services.xinghuo_service import xinghuo_service
from app.services.knowledge_base import knowledge_base
from app.services.nlp_service import nlp_service
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/chat", tags=["聊天"])


# ==================== 辅助函数 ====================

def build_system_prompt(user: User, mode: str = "normal") -> str:
    """
    构建AI学姐系统提示词

    Args:
        user: 当前用户
        mode: 对话模式 (normal/emotion)

    Returns:
        系统提示词字符串
    """
    if mode == "emotion":
        return """你是"AI学姐·心灵陪伴"，广州商学院有温度的倾听者。
先共情后引导，用温暖的语言，不说教、不讲大道理。
当学生表达负面情绪时，先给予理解和接纳，再用积极的方式引导。
记住：你是一个朋友，不是老师。"""

    # 普通模式
    proaudio = None
    if hasattr(user, 'student_proaudio') and user.student_proaudio:
        proaudio = user.student_proaudio

    major = proaudio.major if proaudio and proaudio.major else "未知"
    grade = proaudio.grade if proaudio and proaudio.grade else "X"
    goal = proaudio.goal if proaudio and proaudio.goal else "未设定"

    return f"""你是"AI小商学姐"，广州商学院的智能校园助手。
专业：{major}
年级：大{grade}年级
目标：{goal}

请用友好、专业的语气回答学生的问题。
回答要简洁有建设性，帮助学生解决问题。"""


async def enhance_with_knowledge(query: str) -> str:
    """
    从知识库检索相关内容，添加到上下文中

    Args:
        query: 用户查询文本

    Returns:
        知识库检索到的相关内容，如果无结果则返回空字符串
    """
    try:
        results = knowledge_base.search(query, top_k=3)
        if results:
            context_parts = []
            for r in results:
                content = r.get("content", "")
                if content:
                    context_parts.append(content)

            if context_parts:
                context = "\n\n相关知识：\n" + "\n".join(context_parts)
                logger.info(f"[Chat] Knowledge base found {len(context_parts)} related entries")
                return context
    except Exception as e:
        logger.warning(f"[Chat] Knowledge base search failed: {e}")

    return ""


async def analyze_sentiment(text: str) -> dict:
    """
    调用NLP服务进行情感分析

    Args:
        text: 待分析文本

    Returns:
        情感分析结果字典
    """
    try:
        result = await nlp_service.sentiment_analysis(text)
        logger.info(f"[Chat] Sentiment analysis result: {result}")
        return result
    except Exception as e:
        logger.warning(f"[Chat] Sentiment analysis failed, using default: {e}")
        # 降级处理：返回默认情感分析结果
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "emotion": "normal"
        }


async def get_recent_messages(
    db: AsyncSession,
    conv_id: int,
    limit: int = 10
) -> List[dict]:
    """
    获取会话最近的的消息历史

    Args:
        db: 数据库会话
        conv_id: 会话ID
        limit: 返回消息数量

    Returns:
        消息列表，格式为 [{"role": "user/assistant", "content": "..."}]
    """
    result = await db.execute(
        select(Message)
        .where(
            and_(
                Message.conv_id == conv_id,
                Message.is_deleted == False
            )
        )
        .order_by(desc(Message.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()

    # 反转以按时间正序排列
    messages = list(reversed(messages))

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
        if msg.content
    ]


async def save_message(
    db: AsyncSession,
    conv_id: int,
    role: str,
    content: str,
    content_type: str = "text",
    sentiment: Optional[str] = None,
    tokens_used: Optional[int] = None,
    latency_ms: Optional[int] = None
) -> Message:
    """
    保存消息到数据库

    Args:
        db: 数据库会话
        conv_id: 会话ID
        role: 角色 (user/assistant)
        content: 消息内容
        content_type: 内容类型 (text/voice)
        sentiment: 情感分析结果
        tokens_used: 消耗的token数
        latency_ms: 延迟毫秒数

    Returns:
        创建的Message对象
    """
    message = Message(
        conv_id=conv_id,
        role=role,
        content_type=content_type,
        content=content,
        sentiment=sentiment,
        tokens_used=tokens_used,
        latency_ms=latency_ms
    )
    db.add(message)

    # 更新会话的消息计数
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.message_count += 1

    await db.commit()
    await db.refresh(message)

    logger.info(f"[Chat] Message saved: conv_id={conv_id}, role={role}, content_len={len(content)}")
    return message


def should_suggest_emotion_mode(sentiment_result: dict) -> bool:
    """
    根据情感分析结果判断是否需要切换到心灵陪伴模式

    Args:
        sentiment_result: 情感分析结果

    Returns:
        是否建议切换模式
    """
    sentiment = sentiment_result.get("sentiment", "neutral")
    emotion = sentiment_result.get("emotion", "normal")

    # 负面情绪或检测到需要情感支持的情况
    if sentiment == "negative":
        return True
    if emotion in ["sad", "angry", "fear", "anxious"]:
        return True

    return False


# ==================== API 端点 ====================

@router.post("/message", response_model=ChatResponse)
@handle_app_errors
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    发送消息并获取AI回复

    流程：
    1. 获取或创建会话
    2. 情感分析用户消息
    3. RAG知识库检索
    4. 构建消息列表（含系统提示词）
    5. 调用星火大模型
    6. 保存消息记录
    7. 返回AI回复
    """
    start_time = time.time()
    logger.info(f"[Chat] Chat request: message_len={len(request.message)}, conv_id={request.conv_id}, mode={request.mode}")

    try:
        # 1. 获取或创建会话
        conv_id = request.conv_id
        if conv_id is None:
            # 创建新会话
            conversation = Conversation(
                user_id=current_user.id,
                title=request.message[:50] if len(request.message) > 50 else request.message,
                category=request.category or "general",
                mode=request.mode or "normal",
                message_count=0
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            conv_id = conversation.id
            logger.info(f"[Chat] Created new conversation: {conv_id}")
        else:
            # 验证会话存在且属于当前用户
            result = await db.execute(
                select(Conversation).where(
                    and_(
                        Conversation.id == conv_id,
                        Conversation.user_id == current_user.id,
                        Conversation.is_deleted == False
                    )
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise NotFoundException("Conversation", conv_id)

        # 2. 情感分析（异步，不阻塞主流程）
        sentiment_result = await analyze_sentiment(request.message)
        sentiment = sentiment_result.get("sentiment", "neutral")

        # 检查是否需要建议切换到心灵陪伴模式
        suggest_emotion_mode = should_suggest_emotion_mode(sentiment_result)

        # 3. RAG知识库检索
        knowledge_context = await enhance_with_knowledge(request.message)

        # 4. 构建消息列表
        mode = request.mode or conversation.mode or "normal"
        system_prompt = build_system_prompt(current_user, mode)

        # 添加知识库上下文到系统提示词
        if knowledge_context:
            system_prompt += knowledge_context

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史消息
        history_messages = await get_recent_messages(db, conv_id, limit=10)
        messages.extend(history_messages)

        # 添加当前用户消息
        messages.append({"role": "user", "content": request.message})

        logger.info(f"[Chat] Constructed {len(messages)} messages (system + {len(history_messages)} history + 1 current)")

        # 5. 调用星火大模型
        try:
            reply = await xinghuo_service.chat_completion(
                messages=messages,
                user_id=str(current_user.id)
            )
        except Exception as e:
            logger.error(f"[Chat] Xinghuo service failed: {e}")
            raise ThirdPartyException(
                service="Xinghuo",
                message=f"AI回复生成失败: {str(e)}",
                original_error=e
            )

        # 6. 计算延迟
        latency_ms = int((time.time() - start_time) * 1000)

        # 7. 保存消息
        user_message = await save_message(
            db=db,
            conv_id=conv_id,
            role="user",
            content=request.message,
            sentiment=sentiment
        )

        assistant_message = await save_message(
            db=db,
            conv_id=conv_id,
            role="assistant",
            content=reply,
            sentiment=None,
            latency_ms=latency_ms
        )

        logger.info(f"[Chat] Chat completed: conv_id={conv_id}, latency={latency_ms}ms")

        return ChatResponse(
            conv_id=conv_id,
            message_id=assistant_message.id,
            content=reply,
            sentiment=sentiment,
            audio_url=None,
            tokens_used=None,
            latency_ms=latency_ms
        )

    except HTTPException:
        raise
    except ThirdPartyException:
        raise
    except Exception as e:
        logger.error(f"[Chat] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天服务异常: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
@handle_app_errors
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的会话列表

    按更新时间倒序排列
    """
    logger.info(f"[Chat] Get conversations for user {current_user.id}, skip={skip}, limit={limit}")

    result = await db.execute(
        select(Conversation)
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()

    logger.info(f"[Chat] Found {len(conversations)} conversations")
    return conversations


@router.get("/conversations/{conv_id}", response_model=ChatHistoryResponse)
@handle_app_errors
async def get_conversation_history(
    conv_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话消息历史

    返回会话信息和消息列表
    """
    logger.info(f"[Chat] Get conversation history: {conv_id} for user {current_user.id}")

    # 查询会话
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conv_id,
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation", conv_id)

    # 查询消息
    messages_result = await db.execute(
        select(Message)
        .where(
            and_(
                Message.conv_id == conv_id,
                Message.is_deleted == False
            )
        )
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    messages = messages_result.scalars().all()

    logger.info(f"[Chat] Found conversation with {len(messages)} messages")

    return ChatHistoryResponse(
        conversations=[conversation],
        messages=messages
    )


@router.post("/conversations", response_model=ConversationResponse)
@handle_app_errors
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新会话
    """
    logger.info(f"[Chat] Create conversation for user {current_user.id}")

    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        category=conversation_data.category or "general",
        mode=conversation_data.mode or "normal",
        message_count=0
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    logger.info(f"[Chat] Conversation created: {conversation.id}")
    return conversation


@router.put("/conversations/{conv_id}", response_model=ConversationResponse)
@handle_app_errors
async def update_conversation(
    conv_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新会话标题、模式等
    """
    logger.info(f"[Chat] Update conversation: {conv_id} for user {current_user.id}")

    # 查询会话
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conv_id,
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation", conv_id)

    # 更新字段
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(conversation, field, value)

    await db.commit()
    await db.refresh(conversation)

    logger.info(f"[Chat] Conversation {conv_id} updated")
    return conversation


@router.delete("/conversations/{conv_id}")
@handle_app_errors
async def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除会话（软删除）
    """
    logger.info(f"[Chat] Delete conversation: {conv_id} for user {current_user.id}")

    # 查询会话
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conv_id,
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation", conv_id)

    # 软删除会话
    conversation.is_deleted = True

    # 软删除所有关联消息
    messages_result = await db.execute(
        select(Message).where(Message.conv_id == conv_id)
    )
    messages = messages_result.scalars().all()
    for msg in messages:
        msg.is_deleted = True

    await db.commit()

    logger.info(f"[Chat] Conversation {conv_id} and {len(messages)} messages soft deleted")
    return {"message": "会话已删除"}


@router.get("/messages/{message_id}", response_model=MessageResponse)
@handle_app_errors
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单条消息详情
    """
    logger.info(f"[Chat] Get message: {message_id} for user {current_user.id}")

    # 查询消息，验证所属会话属于当前用户
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.conversation))
        .where(
            and_(
                Message.id == message_id,
                Message.is_deleted == False
            )
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        raise NotFoundException("Message", message_id)

    # 验证会话所属用户
    if message.conversation.user_id != current_user.id:
        raise NotFoundException("Message", message_id)

    return message


@router.post("/voice")
@handle_app_errors
async def chat_voice(
    audio: UploadFile = File(..., description="语音文件"),
    current_user: User = Depends(get_current_user)
):
    """
    语音识别接口 - 将语音转为文字

    用于语音输入：用户说话 -> 识别为文字 -> 输出到输入框

    返回识别后的文字内容
    """
    logger.info(f"[Chat] Voice recognition for user {current_user.id}, filename={audio.filename}")

    # 1. 保存上传的音频文件到临时目录
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "audio")
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一文件名
    file_ext = os.path.splitext(audio.filename or ".wav")[1] or ".wav"
    temp_audio_path = os.path.join(upload_dir, f"{uuid.uuid4().hex}{file_ext}")

    try:
        # 读取并保存文件
        audio_data = await audio.read()
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        logger.info(f"[Chat] Audio file saved: {temp_audio_path}, size: {len(audio_data)} bytes")
    except Exception as e:
        logger.error(f"[Chat] Failed to save audio file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音频文件保存失败: {str(e)}"
        )

    # 2. ASR语音识别
    recognized_text = ""
    try:
        asr_result = await asr_service.recognize_file(temp_audio_path)
        recognized_text = asr_result.get("text", "")
        logger.info(f"[Chat] ASR recognized: {recognized_text[:100]}...")
    except Exception as e:
        logger.error(f"[Chat] ASR failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"语音识别失败: {str(e)}"
        )
    finally:
        # 清理临时文件
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except:
                pass

    # 3. 返回识别结果
    return {
        "success": True,
        "data": {
            "text": recognized_text
        }
    }


@router.post("/tts")
@handle_app_errors
async def chat_tts(
    text: str,
    voice: str = "xiaoyan",
    current_user: User = Depends(get_current_user)
):
    """
    语音合成接口 - 将文字转为语音

    用于AI回复的语音播放：输入文字 -> 合成语音 -> 返回音频URL

    Args:
        text: 要转换的文本（最大2000汉字）
        voice: 发音人，默认为"xiaoyan"（讯飞少女音）

    Returns:
        音频文件URL，可直接用于播放
    """
    logger.info(f"[Chat] TTS request for user {current_user.id}, text length: {len(text)}, voice: {voice}")

    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本内容不能为空"
        )

    try:
        audio_url = await tts_service.synthesize_to_url(
            text=text[:2000],  # 限制最大2000字
            voice=voice
        )
        logger.info(f"[Chat] TTS generated: {audio_url}")
        return {
            "success": True,
            "data": {
                "audio_url": audio_url
            }
        }
    except Exception as e:
        logger.error(f"[Chat] TTS failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"语音合成失败: {str(e)}"
        )


@router.get("/suggestions")
@handle_app_errors
async def get_chat_suggestions(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取对话建议（快捷问题）

    根据用户画像生成个性化建议
    """
    logger.info(f"[Chat] Get chat suggestions for user {current_user.id}")

    # 基础建议
    suggestions = [
        "今天有什么重要的课程安排？",
        "帮我规划一下这周的学习时间",
        "选修课推荐有哪些？",
        "图书馆开放时间是多少？"
    ]

    # 根据用户年级添加个性化建议
    proaudio = None
    if hasattr(current_user, 'student_proaudio') and current_user.student_proaudio:
        proaudio = current_user.student_proaudio

    if proaudio:
        if proaudio.grade == 1:
            suggestions.extend([
                "大学生活和高中有什么不同？",
                "如何适应大学的学习节奏？",
                "有哪些社团可以参加？"
            ])
        elif proaudio.grade == 4:
            suggestions.extend([
                "简历怎么写比较好？",
                "毕业论文开题怎么准备？",
                "找工作要注意什么？"
            ])

    return {
        "success": True,
        "data": {
            "suggestions": suggestions[:6]  # 最多返回6条
        }
    }