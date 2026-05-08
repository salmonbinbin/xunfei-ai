"""
教师通知 API 路由
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.notification import (
    NotificationGenerateRequest,
    NotificationGenerateResponse,
    NotificationSendRequest,
    NotificationGroup,
)
from app.services.notification_service import notification_service

logger = logging.getLogger("notification_api")
router = APIRouter(prefix="/api/teacher/notification", tags=["教师通知"])


@router.post("/generate")
async def generate_notification(
    request: NotificationGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AI生成通知

    - notification_type: 通知类型 (exam/meeting/activity/holiday/submission/other)
    - topic: 通知主题
    - additional_info: 补充信息（可选）
    """
    logger.info(f"[API] ========== generate_notification 开始 ==========")
    logger.info(f"[API] 请求: notification_type={request.notification_type}, topic={request.topic}")
    logger.info(f"[API] 请求: additional_info={request.additional_info}")

    try:
        logger.info(f"[API] 调用 notification_service.generate_notification...")
        result = await notification_service.generate_notification(
            notification_type=request.notification_type,
            topic=request.topic,
            additional_info=request.additional_info
        )
        logger.info(f"[API] generate_notification 成功: result={result}")
        logger.info(f"[API] ========== generate_notification 结束 ==========")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"[API] generate_notification 失败: {type(e).__name__}: {str(e)}", exc_info=True)
        logger.info(f"[API] ========== generate_notification 异常结束 ==========")
        return {
            "success": False,
            "error": {
                "message": f"生成通知失败: {str(e)}"
            }
        }


@router.get("/groups", response_model=List[NotificationGroup])
async def get_notification_groups():
    """
    获取可用的飞书群组
    """
    groups = notification_service.get_available_groups()
    return [NotificationGroup(**g) for g in groups]


@router.post("/send")
async def send_notification(
    request: NotificationSendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送通知到飞书群

    - title: 通知标题
    - content: 通知内容
    - group_id: 群组ID
    """
    logger.info(f"[API] send_notification: group_id={request.group_id}")

    result = notification_service.send_to_feishu(
        title=request.title,
        content=request.content,
        group_id=request.group_id
    )

    if result.get("success"):
        return {"success": True, "message": result.get("message")}
    else:
        raise HTTPException(status_code=500, detail=result.get("message"))
