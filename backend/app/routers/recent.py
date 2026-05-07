"""
最近活动路由

用于"我的"模块获取各模块最近活动时间线数据
"""
from typing import List
from fastapi import APIRouter, Depends, Query
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

router = APIRouter(prefix="/api", tags=["最近活动"])


@router.get("/review/recent", response_model=List[ReviewRecordResponse])
@handle_app_errors
async def get_recent_reviews(
    limit: int = Query(default=3, ge=1, le=10, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近录音回顾

    按创建时间倒序，返回最新limit条已完成的录音
    """
    logger.info(f"[Recent] Get recent reviews | user_id: {current_user.id}, limit: {limit}")

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

    logger.info(f"[Recent] Found {len(records)} recent reviews | user_id: {current_user.id}")
    return [ReviewRecordResponse.model_validate(r) for r in records]


@router.get("/chat/conversations/recent", response_model=List[ConversationResponse])
@handle_app_errors
async def get_recent_conversations(
    limit: int = Query(default=3, ge=1, le=10, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近对话会话

    按更新时间倒序，返回最新limit条会话
    """
    logger.info(f"[Recent] Get recent conversations | user_id: {current_user.id}, limit: {limit}")

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

    logger.info(f"[Recent] Found {len(conversations)} recent conversations | user_id: {current_user.id}")
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/schedule/recent", response_model=List[ScheduleResponse])
@handle_app_errors
async def get_recent_schedules(
    limit: int = Query(default=3, ge=1, le=10, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近日程

    按创建时间倒序，返回最新limit条日程
    """
    logger.info(f"[Recent] Get recent schedules | user_id: {current_user.id}, limit: {limit}")

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

    logger.info(f"[Recent] Found {len(schedules)} recent schedules | user_id: {current_user.id}")
    return [ScheduleResponse.model_validate(s) for s in schedules]
