"""
认证工具模块

提供JWT token生成、验证、密码hash等功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.utils.errors import UnauthorizedException

# 密码hash上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 安全依赖
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码hash"""
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成JWT access token

    Args:
        user_id: 用户ID（整数）
        expires_delta: 可选的过期时间delta

    Returns:
        编码后的JWT token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),  # JWT sub claim must be a string
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证JWT token

    Args:
        token: JWT token字符串

    Returns:
        解码后的token数据

    Raises:
        UnauthorizedException: token无效或已过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise UnauthorizedException(message=f"Token无效: {str(e)}")


def get_user_id_from_token(token: str) -> int:
    """
    从token中提取用户ID

    Args:
        token: JWT token字符串

    Returns:
        用户ID（整数）
    """
    payload = verify_token(token)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise UnauthorizedException(message="Token中缺少用户信息")
    return int(user_id_str)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI依赖：从request中获取当前认证用户

    Args:
        credentials: HTTP Bearer token
        db: 数据库会话

    Returns:
        当前登录的用户对象

    Raises:
        HTTPException: token无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        user_id = get_user_id_from_token(token)
    except UnauthorizedException:
        raise credentials_exception

    # 从数据库查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user
