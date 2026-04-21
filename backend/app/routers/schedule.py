"""
日程路由

日程管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
import logging

from app.database import get_db
from app.models.user import User
from app.models.schedule import Schedule
from app.schemas.timetable import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse
)
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException
from app.services.xinghuo_service import xinghuo_service

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/schedule", tags=["日程"])


@router.get("", response_model=List[ScheduleResponse])
@handle_app_errors
async def get_schedules(
    day_of_week: Optional[int] = None,
    is_completed: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的日程列表

    支持按星期几和完成状态筛选
    """
    logger.info(f"[Schedule] Get schedules for user {current_user.id}, day_of_week: {day_of_week}")

    # 构建查询
    query = select(Schedule).where(
        and_(
            Schedule.user_id == current_user.id,
            Schedule.is_deleted == False
        )
    )

    if day_of_week is not None:
        query = query.where(Schedule.day_of_week == day_of_week)

    if is_completed is not None:
        query = query.where(Schedule.is_completed == is_completed)

    query = query.offset(skip).limit(limit).order_by(Schedule.day_of_week, Schedule.time_desc)

    result = await db.execute(query)
    schedules = result.scalars().all()

    logger.info(f"[Schedule] Found {len(schedules)} schedules")
    return schedules


@router.get("/{schedule_id}", response_model=ScheduleResponse)
@handle_app_errors
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取日程详情
    """
    logger.info(f"[Schedule] Get schedule: {schedule_id} for user {current_user.id}")

    result = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.id == schedule_id,
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise NotFoundException("Schedule", schedule_id)

    return schedule


@router.post("", response_model=ScheduleResponse)
@handle_app_errors
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建日程 - 支持自然语言

    如果只有message字段，调用星火意图识别解析
    如果有结构化字段，直接创建
    """
    logger.info(f"[Schedule] Create schedule: {schedule_data.event} for user {current_user.id}")

    # 检查是否需要意图识别（只有event字段，没有结构化信息）
    needs_intent_recognition = (
        schedule_data.day_of_week is None and
        schedule_data.time_desc is None and
        schedule_data.event_type == "日程"
    )

    if needs_intent_recognition:
        try:
            # 调用星火意图识别
            intent_result = await xinghuo_service.intent_recognition(
                text=schedule_data.event,
                user_id=str(current_user.id)
            )

            logger.info(f"[Schedule] Intent recognition result: {intent_result}")

            # 使用识别结果创建日程
            schedule = Schedule(
                user_id=current_user.id,
                event=intent_result.get("event", schedule_data.event),
                event_type=intent_result.get("event_type", schedule_data.event_type or "日程"),
                day_of_week=intent_result.get("day_of_week"),
                time_desc=intent_result.get("time_desc"),
                location=intent_result.get("location"),
                is_completed=0
            )
        except Exception as e:
            logger.warning(f"[Schedule] Intent recognition failed: {e}, creating with original data")
            # 意图识别失败，使用原始数据
            schedule = Schedule(
                user_id=current_user.id,
                event=schedule_data.event,
                event_type=schedule_data.event_type or "日程",
                day_of_week=schedule_data.day_of_week,
                time_desc=schedule_data.time_desc,
                location=schedule_data.location,
                is_completed=0
            )
    else:
        # 使用结构化数据创建
        schedule = Schedule(
            user_id=current_user.id,
            event=schedule_data.event,
            event_type=schedule_data.event_type or "日程",
            day_of_week=schedule_data.day_of_week,
            time_desc=schedule_data.time_desc,
            location=schedule_data.location,
            is_completed=0
        )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    logger.info(f"[Schedule] Schedule created with id: {schedule.id}")
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
@handle_app_errors
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新日程
    """
    logger.info(f"[Schedule] Update schedule: {schedule_id} for user {current_user.id}")

    # 查询日程
    result = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.id == schedule_id,
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise NotFoundException("Schedule", schedule_id)

    # 更新字段
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    await db.commit()
    await db.refresh(schedule)

    logger.info(f"[Schedule] Schedule {schedule_id} updated")
    return schedule


@router.delete("/{schedule_id}")
@handle_app_errors
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    软删除日程
    """
    logger.info(f"[Schedule] Delete schedule: {schedule_id} for user {current_user.id}")

    # 查询日程
    result = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.id == schedule_id,
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise NotFoundException("Schedule", schedule_id)

    # 软删除
    schedule.is_deleted = True
    await db.commit()

    logger.info(f"[Schedule] Schedule {schedule_id} soft deleted")
    return {"message": "日程已删除"}


@router.put("/{schedule_id}/complete")
@handle_app_errors
async def complete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    标记日程完成
    """
    logger.info(f"[Schedule] Complete schedule: {schedule_id} for user {current_user.id}")

    # 查询日程
    result = await db.execute(
        select(Schedule).where(
            and_(
                Schedule.id == schedule_id,
                Schedule.user_id == current_user.id,
                Schedule.is_deleted == False
            )
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise NotFoundException("Schedule", schedule_id)

    # 标记为已完成
    schedule.is_completed = 1
    await db.commit()

    logger.info(f"[Schedule] Schedule {schedule_id} marked as completed")
    return {"message": "日程已完成"}
