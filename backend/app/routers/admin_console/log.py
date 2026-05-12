"""
操作日志路由
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import logging
from jose import jwt

from app.database import get_db
from app.models import AdminLog
from app.utils.errors import handle_app_errors
from app.config import settings
from app.services.xinghuo_service import XingHuoService

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/admin/logs", tags=["管理端-操作日志"])

# Action value to Chinese label mapping
ACTION_TEXT_MAP = {
    "login": "管理员登录",
    "logout": "管理员登出",
    "user.disable": "禁用用户",
    "user.enable": "启用用户",
    "user.export": "导出用户数据",
    "user.view": "查看用户详情",
    "log.view": "查看操作日志",
    "dashboard.view": "查看数据看板"
}


def get_action_text(action: str) -> str:
    """Map action value to Chinese label"""
    return ACTION_TEXT_MAP.get(action, action)


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
        logger.error(f"[Logs] Token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")


@router.get("")
@handle_app_errors
async def get_logs(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    action: Optional[str] = None,
    admin_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志列表"""
    current_admin_id = get_current_admin_id(request)
    logger.info(f"[Logs] Get logs, admin_id={current_admin_id}, page={page}")

    # 处理admin_id空字符串
    try:
        admin_id_int = int(admin_id) if admin_id else None
    except ValueError:
        admin_id_int = None

    try:
        # 构建查询条件
        conditions = []
        if start_date:
            conditions.append(AdminLog.created_at >= f"{start_date} 00:00:00")
        if end_date:
            conditions.append(AdminLog.created_at <= f"{end_date} 23:59:59")
        if action:
            conditions.append(AdminLog.action == action)
        if admin_id_int:
            conditions.append(AdminLog.admin_id == admin_id_int)

        # 获取总数
        count_query = select(func.count(AdminLog.id))
        if conditions:
            count_query = count_query.where(*conditions)
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # 获取分页数据
        offset = (page - 1) * page_size
        query = (
            select(AdminLog)
            .where(*conditions)
            .order_by(AdminLog.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        items = []
        for log in logs:
            items.append({
                "id": log.id,
                "admin_id": log.admin_id,
                "admin_name": log.admin_name,
                "action": log.action,
                "action_text": log.action_text or get_action_text(log.action),
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })

        logger.info(f"[Logs] Fetched {len(items)} logs, total={total}")

        return {
            "success": True,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }

    except Exception as e:
        logger.error(f"[Logs] Error fetching logs: {e}", exc_info=True)
        return {
            "success": True,
            "data": {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        }


@router.get("/actions")
@handle_app_errors
async def get_log_actions(request: Request, db: AsyncSession = Depends(get_db)):
    """获取操作类型枚举"""
    admin_id = get_current_admin_id(request)
    logger.debug(f"[Logs] Get action types, admin_id={admin_id}")

    actions = [
        {"value": "login", "label": "管理员登录"},
        {"value": "logout", "label": "管理员登出"},
        {"value": "user.disable", "label": "禁用用户"},
        {"value": "user.enable", "label": "启用用户"},
        {"value": "user.export", "label": "导出用户数据"},
        {"value": "user.view", "label": "查看用户详情"},
        {"value": "log.view", "label": "查看操作日志"},
        {"value": "dashboard.view", "label": "查看数据看板"}
    ]

    return {
        "success": True,
        "data": actions
    }


@router.post("/analyze")
@handle_app_errors
async def analyze_logs(request: Request, db: AsyncSession = Depends(get_db)):
    """AI智能分析最近7天操作日志"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Logs] Analyze logs, admin_id={admin_id}")

    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Query logs from last 7 days
    query = select(AdminLog).where(AdminLog.created_at >= seven_days_ago)
    result = await db.execute(query)
    logs = result.scalars().all()

    total_count = len(logs)

    # If no logs, return simple message
    if total_count == 0:
        return {
            "success": True,
            "data": {
                "summary": "近7天无操作记录",
                "total_count": 0,
                "top_actions": [],
                "peak_hour": None,
                "trend": []
            }
        }

    # Aggregate statistics
    action_counts = {}
    hourly_counts = {}
    daily_counts = {}

    for log in logs:
        # Action counts
        action = log.action or "unknown"
        action_counts[action] = action_counts.get(action, 0) + 1

        # Hourly distribution
        if log.created_at:
            hour = log.created_at.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

            # Daily counts
            date_str = log.created_at.strftime("%Y-%m-%d")
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

    # Calculate TOP 3 action types
    sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
    top_actions = [
        {"action": action, "action_text": get_action_text(action), "count": count}
        for action, count in sorted_actions[:3]
    ]

    # Calculate peak hour
    peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None

    # Calculate active days (days with at least one operation)
    active_days = len([d for d in daily_counts.values() if d > 0])

    # Calculate 7-day trend (fill in missing days with 0)
    trend = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        trend.append({"date": date, "count": daily_counts.get(date, 0)})

    # Build detailed stats for AI
    action_details = "\n".join([f"- {get_action_text(a)}: {c}次" for a, c in sorted_actions[:5]])

    # Calculate comparison with average
    avg_per_day = total_count / 7 if total_count > 0 else 0
    today_count = daily_counts.get(datetime.now().strftime("%Y-%m-%d"), 0)

    # Determine activity level
    if avg_per_day > 20:
        activity_level = "非常活跃"
    elif avg_per_day > 10:
        activity_level = "比较活跃"
    elif avg_per_day > 5:
        activity_level = "一般活跃"
    else:
        activity_level = "较少操作"

    # Generate AI summary with more detail
    detail_stats = f"""近7天操作数据：
- 总操作次数：{total_count}次
- 活跃天数：{active_days}天
- 日均操作：{avg_per_day:.1f}次
- 今日操作：{today_count}次
- 高峰时段：{peak_hour}点
- 操作类型分布：
{action_details}"""

    try:
        xinghuo = XingHuoService()
        prompt = f"""你是数据分析助手。请分析以下管理员操作数据，用2-3句话概括：
{detail_stats}

分析要点：
1. 管理员的整体活动水平
2. 是否有异常模式（如某天操作量突然增加/减少）
3. 主要操作偏好

请用简洁的中文回答，不超过80字。"""

        messages = [{"role": "user", "content": prompt}]
        ai_summary = await xinghuo.chat_completion(messages, user_id=str(admin_id), max_tokens=200)
        summary = ai_summary.strip()[:150] if ai_summary else f"管理员活动{activity_level}，共{total_count}次操作，日均{avg_per_day:.1f}次。"
    except Exception as e:
        logger.warning(f"[Logs] AI summary failed: {e}")
        summary = f"管理员活动{activity_level}，共{total_count}次操作，日均{avg_per_day:.1f}次，峰值出现在{peak_hour}点。"

    logger.info(f"[Logs] Analysis complete: total={total_count}, peak_hour={peak_hour}")

    return {
        "success": True,
        "data": {
            "summary": summary,
            "total_count": total_count,
            "top_actions": top_actions,
            "peak_hour": peak_hour,
            "active_days": active_days,
            "trend": trend
        }
    }