"""
数据看板路由
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, distinct, and_, select, text
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging
from jose import jwt

from app.database import get_db
from app.utils.errors import handle_app_errors
from app.config import settings
from app.models import UserLog, LoginLog, ApiLog

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/admin/dashboard", tags=["管理端-数据看板"])


def get_current_admin_id(request: Request) -> int:
    """从请求中获取当前管理员ID"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")

    token = auth_header[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id = int(payload.get("sub", 0))
        if payload.get("type") != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")
        return admin_id
    except Exception as e:
        logger.error(f"[Dashboard] Token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")


@router.get("/stats")
@handle_app_errors
async def get_dashboard_stats(request: Request, db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Dashboard] Get stats, admin_id={admin_id}")

    today = date.today()
    start_of_day = f"{today} 00:00:00"
    end_of_day = f"{today} 23:59:59"

    try:
        # 今日在线人数（去重登录用户）
        result = await db.execute(
            select(func.count(distinct(LoginLog.user_id)))
            .where(LoginLog.created_at >= start_of_day, LoginLog.created_at <= end_of_day)
        )
        online_users = result.scalar() or 0

        # 今日登录学生数
        result = await db.execute(
            select(func.count(distinct(LoginLog.user_id)))
            .where(
                LoginLog.created_at >= start_of_day,
                LoginLog.created_at <= end_of_day,
                LoginLog.user_type == "student"
            )
        )
        student_logins = result.scalar() or 0

        # 今日登录教师数
        result = await db.execute(
            select(func.count(distinct(LoginLog.user_id)))
            .where(
                LoginLog.created_at >= start_of_day,
                LoginLog.created_at <= end_of_day,
                LoginLog.user_type == "teacher"
            )
        )
        teacher_logins = result.scalar() or 0

        # API调用总量
        result = await db.execute(
            select(func.count(ApiLog))
            .where(ApiLog.created_at >= start_of_day, ApiLog.created_at <= end_of_day)
        )
        api_calls = result.scalar() or 0

        # 功能使用排行（TOP5）
        result = await db.execute(
            select(UserLog.module, func.count(UserLog.id).label("count"))
            .where(UserLog.created_at >= start_of_day, UserLog.created_at <= end_of_day)
            .group_by(UserLog.module)
            .order_by(func.count(UserLog.id).desc())
            .limit(5)
        )
        module_ranking = []
        module_name_map = {
            "ai_sister": "AI学姐对话",
            "review": "录音回顾",
            "timetable": "课表管理",
            "translate": "智能翻译",
            "course_advisor": "选课助手",
            "activity": "校园活动",
            "grade": "成绩管理",
            "notification": "通知发布",
            "lesson_plan": "备课教案"
        }
        for row in result.fetchall():
            module_ranking.append({
                "module": row.module,
                "name": module_name_map.get(row.module, row.module),
                "count": row.count
            })

        # API调用统计
        result = await db.execute(
            select(
                ApiLog.api_name,
                func.count(ApiLog.id).label("count"),
                func.sum(func.cast(ApiLog.call_type == "fail", Integer)).label("fail_count"),
                func.round(func.sum(func.cast(ApiLog.call_type == "fail", Integer)) / func.count(ApiLog.id) * 100, 2).label("fail_rate")
            )
            .where(ApiLog.created_at >= start_of_day, ApiLog.created_at <= end_of_day)
            .group_by(ApiLog.api_name)
        )
        api_stats = []
        api_name_map = {
            "asr": "语音识别",
            "tts": "语音合成",
            "spark": "星火大模型",
            "ocr": "文字识别",
            "nlp": "NLP分析",
            "ppt": "智能PPT"
        }
        for row in result.fetchall():
            api_stats.append({
                "api_name": row.api_name,
                "name": api_name_map.get(row.api_name, row.api_name),
                "count": row.count,
                "fail_count": row.fail_count,
                "fail_rate": row.fail_rate
            })

        logger.info(f"[Dashboard] Stats fetched: online={online_users}, api_calls={api_calls}")

        return {
            "success": True,
            "data": {
                "today_online_users": online_users,
                "today_student_logins": student_logins,
                "today_teacher_logins": teacher_logins,
                "today_api_calls": api_calls,
                "module_ranking": module_ranking,
                "api_stats": api_stats,
                "date": today.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"[Dashboard] Error fetching stats: {e}", exc_info=True)
        return {
            "success": True,
            "data": {
                "today_online_users": 0,
                "today_student_logins": 0,
                "today_teacher_logins": 0,
                "today_api_calls": 0,
                "module_ranking": [],
                "api_stats": [],
                "date": date.today().isoformat()
            }
        }


@router.get("/trend")
@handle_app_errors
async def get_hourly_trend(request: Request, date: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """获取小时趋势数据"""
    admin_id = get_current_admin_id(request)
    target_date = date or date.today().isoformat()
    logger.info(f"[Dashboard] Get trend for {target_date}, admin_id={admin_id}")

    try:
        result = await db.execute(
            select(
                text("HOUR(created_at) as hour"),
                func.count(text("DISTINCT user_id")).label("user_count")
            )
            .where(text(f"DATE(created_at) = '{target_date}'"))
            .group_by(text("HOUR(created_at)"))
            .order_by(text("HOUR(created_at)"))
        )
        hours = []
        for row in result.fetchall():
            hours.append({
                "hour": row.hour,
                "user_count": row.user_count
            })

        return {
            "success": True,
            "data": {
                "date": target_date,
                "hours": hours
            }
        }
    except Exception as e:
        logger.error(f"[Dashboard] Error fetching trend: {e}", exc_info=True)
        hours = [{"hour": h, "user_count": 0} for h in range(24)]
        return {
            "success": True,
            "data": {
                "date": target_date,
                "hours": hours
            }
        }