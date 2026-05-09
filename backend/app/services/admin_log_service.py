"""
管理员操作日志服务

用于记录管理员在管理端的操作行为
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models.admin_log import AdminLog

logger = logging.getLogger("admin_log")


async def save_admin_log(
    admin_id: int,
    admin_name: str,
    action: str,
    action_text: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    detail: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[int]:
    """
    保存管理员操作日志

    Args:
        admin_id: 管理员ID
        admin_name: 管理员昵称（冗余存储）
        action: 操作类型 (user.disable, user.enable, user.export, user.view, log.view, dashboard.view)
        action_text: 操作描述
        target_type: 操作对象类型
        target_id: 操作对象ID
        detail: 详细信息（JSON）
        ip_address: IP地址
        user_agent: 浏览器信息

    Returns:
        日志记录ID，失败返回None
    """
    try:
        async with AsyncSessionLocal() as db:
            # 将detail字典转为JSON字符串存储
            detail_str = json.dumps(detail, ensure_ascii=False) if detail else None

            log = AdminLog(
                admin_id=admin_id,
                admin_name=admin_name,
                action=action,
                action_text=action_text,
                target_type=target_type,
                target_id=target_id,
                detail=detail_str,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            logger.info(f"[AdminLog] Saved: admin_id={admin_id}, action={action}")
            return log.id
    except Exception as e:
        logger.error(f"[AdminLog] Failed to save log: {e}", exc_info=True)
        return None


def get_action_name(action: str) -> str:
    """获取操作类型中文名称"""
    action_map = {
        "user.disable": "禁用用户",
        "user.enable": "启用用户",
        "user.export": "导出用户数据",
        "user.view": "查看用户详情",
        "log.view": "查看操作日志",
        "dashboard.view": "查看数据看板"
    }
    return action_map.get(action, action)
