"""
"我的"模块路由

用户个人中心相关API，包括最近活动时间线
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import logging

from app.database import get_db
from app.models.user import User
from app.models.review import ReviewRecord
from app.models.chat import Conversation
from app.models.schedule import Schedule
from app.schemas.review import ReviewRecordResponse
from app.schemas.chat import ConversationResponse
from app.schemas.timetable import ScheduleResponse
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/profile", tags=["我的"])


@router.get("/review/recent", response_model=List[ReviewRecordResponse])
@handle_app_errors
async def get_recent_reviews(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近录音回顾

    按创建时间倒序，返回最新limit条已完成的录音
    """
    logger.info(f"[Profile] Get recent reviews | user_id: {current_user.id}, limit: {limit}")

    query = (
        select(ReviewRecord)
        .where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False,
                ReviewRecord.status == "completed"
            )
        )
        .order_by(desc(ReviewRecord.created_at))
        .limit(limit)
    )

    result = await db.execute(query)
    records = result.scalars().all()

    logger.info(f"[Profile] Found {len(records)} recent reviews | user_id: {current_user.id}")
    return [ReviewRecordResponse.model_validate(r) for r in records]


@router.get("/chat/conversations/recent", response_model=List[ConversationResponse])
@handle_app_errors
async def get_recent_conversations(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近对话会话

    按更新时间倒序，返回最新limit条会话
    """
    logger.info(f"[Profile] Get recent conversations | user_id: {current_user.id}, limit: {limit}")

    query = (
        select(Conversation)
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
    )

    result = await db.execute(query)
    conversations = result.scalars().all()

    logger.info(f"[Profile] Found {len(conversations)} recent conversations | user_id: {current_user.id}")
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/schedule/recent", response_model=List[ScheduleResponse])
@handle_app_errors
async def get_recent_schedules(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近日程

    按创建时间倒序，返回最新limit条日程
    """
    logger.info(f"[Profile] Get recent schedules | user_id: {current_user.id}, limit: {limit}")

    query = (
        select(Schedule)
        .where(
            and_(
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
        .order_by(desc(Schedule.created_at))
        .limit(limit)
    )

    result = await db.execute(query)
    schedules = result.scalars().all()

    logger.info(f"[Profile] Found {len(schedules)} recent schedules | user_id: {current_user.id}")
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get("/stats")
@handle_app_errors
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户数据统计

    返回各模块的数量统计：
    - courses: 课程数量
    - reviews: 录音回顾数量
    - conversations: 对话会话数量
    - schedules: 日程数量
    """
    logger.info(f"[Profile] Get profile stats | user_id: {current_user.id}")

    # 获取录音回顾数量
    reviews_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    reviews_count = len(reviews_result.scalars().all())

    # 获取对话会话数量
    conversations_result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.is_deleted == False
            )
        )
    )
    conversations_count = len(conversations_result.scalars().all())

    # 获取日程数量
    schedules_result = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
    )
    schedules_count = len(schedules_result.scalars().all())

    logger.info(f"[Profile] Stats retrieved | user_id: {current_user.id}, reviews: {reviews_count}, conversations: {conversations_count}, schedules: {schedules_count}")

    return {
        "success": True,
        "data": {
            "reviews": reviews_count,
            "conversations": conversations_count,
            "schedules": schedules_count
        }
    }
