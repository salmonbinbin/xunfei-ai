"""
校园活动助手路由

活动策划方案生成、宣传文案生成、飞书群推送
"""
from typing import List, Dict
from fastapi import APIRouter, Depends
import logging

from app.models.user import User
from app.schemas.activity import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    GenerateCopyRequest,
    GenerateCopyResponse,
    SendFeishuRequest,
    SendFeishuResponse,
    AvailableGroupsResponse,
)
from app.services.feishu_service import feishu_service
from app.services.xinghuo_service import xinghuo_service
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, ValidationException
from app.config import settings

logger = logging.getLogger("activity")

router = APIRouter(prefix="/api/activity", tags=["校园活动助手"])


# ============ 生成活动策划方案 ============

@router.post("/generate-plan", response_model=GeneratePlanResponse)
@handle_app_errors
async def generate_activity_plan(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成活动策划方案

    基于活动基本信息，AI生成完整的活动策划方案，包含：
    - 活动概述
    - 时间安排
    - 人员分工
    - 预算清单
    - 风险预案
    - 宣传方案
    """
    logger.info(
        f"[Activity] Generate plan request - user: {current_user.id}, "
        f"type: {request.activity_type}, theme: {request.theme}"
    )

    # 构造Prompt
    special_needs_text = ""
    if request.special_needs:
        special_needs_text = "\n".join([f"- {need}" for need in request.special_needs])

    prompt = f"""你是校园活动策划专家。请为以下活动生成完整的策划方案。

【活动基本信息】
- 活动类型：{request.activity_type}
- 活动主题：{request.theme}
- 预计人数：{request.scale}
- 预算范围：{request.budget}
- 活动时间：{request.activity_time or '待定'}

{f'【特殊需求】\n{special_needs_text}' if special_needs_text else ''}

请严格按照以下格式生成策划方案（直接输出，不要加标题前缀）：

【活动名称】：{request.theme}
【活动概述】：简要描述活动目的和意义

【时间安排】
  - 前期准备：...
  - 活动当天：...
  - 后期收尾：...

【人员分工】
  - 策划组：...
  - 宣传组：...
  - 后勤组：...
  - 机动组：...

【预算清单】
  - 奖品：...
  - 物料：...
  - 预计总支出：...

【风险预案】
  - 风险1：应对措施
  - 风险2：应对措施

【宣传方案】
  - 线上：...
  - 线下：...

请确保方案内容详实、可操作性强。"""

    messages = [{"role": "user", "content": prompt}]
    plan = await xinghuo_service.chat_completion(
        messages=messages,
        user_id=str(current_user.id),
        temperature=0.7,
        max_tokens=4096
    )

    logger.info(f"[Activity] Plan generated for user {current_user.id}, length: {len(plan)}")

    return GeneratePlanResponse(
        success=True,
        plan=plan,
        message="策划方案生成成功"
    )


# ============ 生成宣传文案 ============

@router.post("/generate-copy", response_model=GenerateCopyResponse)
@handle_app_errors
async def generate_promotional_copy(
    request: GenerateCopyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成宣传文案

    基于活动信息，AI生成多种类型的宣传文案：
    - 海报主标题（5-15字）
    - 朋友圈短文案（50-100字）
    - 公众号推文（300-500字）
    - 邀请函（200-300字）
    - 广播稿（100-200字）
    """
    logger.info(
        f"[Activity] Generate copy request - user: {current_user.id}, "
        f"type: {request.copy_type}, style: {request.style}"
    )

    # 根据文案类型确定输出要求
    copy_type_requirements = {
        "海报主标题": "5-15字，简短有力、朗朗上口，适合制作海报",
        "朋友圈短文案": "50-100字，活泼、有emoji，适合朋友圈/QQ空间",
        "公众号推文": "300-500字，完整、有吸引力，适合公众号/抖音描述",
        "邀请函": "200-300字，正式、格式规范，适合正式邀请嘉宾/领导",
        "广播稿": "100-200字，口语化、有节奏，适合学校广播站"
    }

    # 根据风格确定语气
    style_tones = {
        "正式严肃": "语气正式庄重，使用正式书面语",
        "活泼青春": "语气活泼开朗，充满青春活力",
        "温情暖心": "语气温暖亲切，传递温暖情感",
        "燃系热血": "语气激昂热血，充满激情动力"
    }

    requirements = copy_type_requirements.get(
        request.copy_type,
        "内容完整、语言流畅"
    )
    tone = style_tones.get(request.style, "语气适中")

    prompt = f"""你是校园宣传文案专家。请为以下活动生成宣传文案。

【活动名称】：{request.activity_name}
【活动概述】：{request.activity_content or '精彩校园活动等你参与'}
【文案类型】：{request.copy_type}
【文案要求】：{requirements}
【语气风格】：{tone}

请直接输出文案内容，不要添加标题或说明文字。

{f"参考活动内容：\n{request.activity_content}" if request.activity_content else ''}"""

    messages = [{"role": "user", "content": prompt}]
    copy = await xinghuo_service.chat_completion(
        messages=messages,
        user_id=str(current_user.id),
        temperature=0.8,
        max_tokens=2048
    )

    logger.info(f"[Activity] Copy generated for user {current_user.id}, length: {len(copy)}")

    return GenerateCopyResponse(
        success=True,
        copy=copy,
        copy_type=request.copy_type,
        style=request.style,
        message="文案生成成功"
    )


# ============ 发送到飞书群 ============

@router.post("/send-feishu", response_model=SendFeishuResponse)
@handle_app_errors
async def send_to_feishu(
    request: SendFeishuRequest,
    current_user: User = Depends(get_current_user)
):
    """
    发送文案到飞书群

    将生成的宣传文案发送到预配置的飞书群。
    群组选项：学生会通知、社团联盟、班级通知、团委通知、宿舍管理
    """
    logger.info(
        f"[Activity] Send to Feishu - user: {current_user.id}, "
        f"group: {request.group_id}"
    )

    # 验证群组ID
    valid_groups = list(settings.FEISHU_GROUPS.keys())
    if request.group_id not in valid_groups:
        raise ValidationException(
            message=f"无效的群组ID：{request.group_id}",
            details={"valid_groups": valid_groups}
        )

    # 获取群组名称
    group_name = settings.FEISHU_GROUPS.get(request.group_id, request.group_id)

    # 发送消息
    result = feishu_service.send_post(
        title=request.title,
        content=request.content,
        group_id=request.group_id
    )

    if not result.get("success"):
        logger.error(
            f"[Activity] Send to Feishu failed - user: {current_user.id}, "
            f"group: {request.group_id}, error: {result.get('error')}"
        )
        return SendFeishuResponse(
            success=False,
            message=result.get("error", "发送失败"),
            group_id=request.group_id,
            group_name=group_name
        )

    logger.info(
        f"[Activity] Send to Feishu success - user: {current_user.id}, "
        f"group: {request.group_id}"
    )

    return SendFeishuResponse(
        success=True,
        message="消息发送成功",
        group_id=request.group_id,
        group_name=group_name
    )


# ============ 获取可用群组列表 ============

@router.get("/groups", response_model=AvailableGroupsResponse)
@handle_app_errors
async def get_available_groups(
    current_user: User = Depends(get_current_user)
):
    """
    获取可用的飞书群组列表

    返回所有预配置的群组信息，供前端展示选择。
    """
    logger.info(f"[Activity] Get available groups - user: {current_user.id}")

    groups = [
        {"id": group_id, "name": group_name}
        for group_id, group_name in settings.FEISHU_GROUPS.items()
    ]

    return AvailableGroupsResponse(
        success=True,
        groups=groups
    )
