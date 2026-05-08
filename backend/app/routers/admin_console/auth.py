"""
管理员认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
import bcrypt

from app.database import get_db
from app.models import Admin, AdminLog
from app.utils.errors import handle_app_errors
from app.config import settings
from jose import jwt

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/admin", tags=["管理端-认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool = True
    token: str
    admin: dict


def create_admin_token(admin_id: int, username: str, role: str) -> str:
    """创建管理员JWT token"""
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": str(admin_id),
        "username": username,
        "role": role,
        "exp": expire,
        "type": "admin"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/login")
@handle_app_errors
async def login(request: LoginRequest, req: Request, db: AsyncSession = Depends(get_db)):
    """管理员登录"""
    logger.info(f"[AdminAuth] Login attempt: {request.username}")

    # 查找管理员
    result = await db.execute(select(Admin).where(Admin.username == request.username, Admin.is_deleted == 0))
    admin = result.scalar_one_or_none()

    if not admin:
        logger.warning(f"[AdminAuth] Login failed: user not found - {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    try:
        stored_hash = admin.password if isinstance(admin.password, bytes) else admin.password.encode('utf-8')
        if not bcrypt.checkpw(request.password.encode('utf-8'), stored_hash):
            logger.warning(f"[AdminAuth] Login failed: wrong password - {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
    except Exception as e:
        logger.error(f"[AdminAuth] Password verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查状态
    if admin.status == "disabled":
        logger.warning(f"[AdminAuth] Login failed: account disabled - {request.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 更新登录信息
    await db.execute(
        update(Admin).where(Admin.id == admin.id).values(
            last_login=datetime.now(),
            login_count=Admin.login_count + 1
        )
    )
    await db.commit()

    # 创建token
    token = create_admin_token(admin.id, admin.username, admin.role)

    # 记录操作日志
    log = AdminLog(
        admin_id=admin.id,
        admin_name=admin.nickname,
        action="login",
        action_text="管理员登录",
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent")
    )
    db.add(log)
    await db.commit()

    logger.info(f"[AdminAuth] Login success: {request.username}")

    return {
        "success": True,
        "data": {
            "token": token,
            "admin": {
                "id": admin.id,
                "username": admin.username,
                "nickname": admin.nickname,
                "role": admin.role
            }
        }
    }


@router.post("/logout")
@handle_app_errors
async def logout(req: Request, db: AsyncSession = Depends(get_db)):
    """管理员登出"""
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            admin_id = int(payload.get("sub", 0))
            if admin_id > 0:
                logger.info(f"[AdminAuth] Admin logout: id={admin_id}")
        except Exception as e:
            logger.warning(f"[AdminAuth] Logout token decode error: {e}")

    return {"success": True, "message": "登出成功"}


@router.get("/profile")
@handle_app_errors
async def get_profile(req: Request, db: AsyncSession = Depends(get_db)):
    """获取当前管理员信息"""
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未授权")

    token = auth_header[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id = int(payload.get("sub", 0))
        if payload.get("type") != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌类型")
    except Exception as e:
        logger.error(f"[AdminAuth] Token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")

    result = await db.execute(select(Admin).where(Admin.id == admin_id, Admin.is_deleted == 0))
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员不存在")

    return {
        "success": True,
        "data": {
            "id": admin.id,
            "username": admin.username,
            "nickname": admin.nickname,
            "role": admin.role,
            "status": admin.status,
            "created_at": admin.created_at.isoformat() if admin.created_at else None
        }
    }