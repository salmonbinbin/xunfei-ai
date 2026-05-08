"""
操作日志路由
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging
from jose import jwt

from app.database import get_db
from app.models import AdminLog
from app.utils.errors import handle_app_errors
from app.config import settings

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/admin/logs", tags=["管理端-操作日志"])


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
    admin_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志列表"""
    current_admin_id = get_current_admin_id(request)
    logger.info(f"[Logs] Get logs, admin_id={current_admin_id}, page={page}")

    try:
        # 构建查询条件
        conditions = []
        if start_date:
            conditions.append(AdminLog.created_at >= f"{start_date} 00:00:00")
        if end_date:
            conditions.append(AdminLog.created_at <= f"{end_date} 23:59:59")
        if action:
            conditions.append(AdminLog.action == action)
        if admin_id:
            conditions.append(AdminLog.admin_id == admin_id)

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
                "action_text": log.action_text,
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