"""
登录日志服务

用于记录用户登录行为
"""
import logging
from typing import Optional
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models.user_log import LoginLog

logger = logging.getLogger("login_log")


async def save_login_log(
    user_id: int,
    user_type: str,
    login_method: str = "phone",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[int]:
    """
    保存登录日志

    Args:
        user_id: 用户ID
        user_type: 用户类型 (student/teacher)
        login_method: 登录方式 (phone, wechat, admin)
        ip_address: IP地址
        user_agent: 浏览器信息

    Returns:
        日志记录ID，失败返回None
    """
    try:
        async with AsyncSessionLocal() as db:
            log = LoginLog(
                user_id=user_id,
                user_type=user_type,
                login_method=login_method,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            logger.info(f"[LoginLog] Saved: user_id={user_id}, user_type={user_type}, method={login_method}")
            return log.id
    except Exception as e:
        logger.error(f"[LoginLog] Failed to save log: {e}", exc_info=True)
        return None
