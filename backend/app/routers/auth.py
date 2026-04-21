"""
认证路由

用户登录、注册、JWT Token管理、学生画像
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User, StudentProfile
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    UserResponse,
    ProfileRequest,
    UserDetailResponse,
    StudentProfileResponse,
)
from app.utils.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException
from app.config import settings

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
@handle_app_errors
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录（账号密码）

    1. 使用用户名（手机号）查找用户
    2. 验证密码
    3. 生成JWT token返回
    """
    logger.info(f"[Auth] Login attempt for username: {login_data.username}")

    # 使用手机号查找用户
    result = await db.execute(select(User).where(User.phone == login_data.username))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(f"[Auth] Login failed - user not found: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"[Auth] Login failed - wrong password for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # 检查是否有学生画像
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    has_profile = profile_result.scalar_one_or_none() is not None

    # 生成JWT token
    access_token = create_access_token(user_id=user.id)

    logger.info(f"[Auth] User logged in successfully: id={user.id}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            has_profile=has_profile
        )
    )


@router.post("/register", response_model=LoginResponse)
@handle_app_errors
async def register(register_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册

    1. 检查手机号是否已存在
    2. 创建新用户（密码加密存储）
    3. 生成JWT token返回
    """
    logger.info(f"[Auth] Register attempt for username: {register_data.username}")

    # 检查手机号是否已存在
    result = await db.execute(select(User).where(User.phone == register_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        logger.warning(f"[Auth] Register failed - phone already exists: {register_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册，请直接登录"
        )

    # 密码哈希
    password_hash = get_password_hash(register_data.password)

    # 创建新用户
    user = User(
        phone=register_data.username,
        password_hash=password_hash,
        nickname=register_data.nickname or f"用户{register_data.username[-4:]}",
        is_active=1
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 生成JWT token
    access_token = create_access_token(user_id=user.id)

    logger.info(f"[Auth] User registered successfully: id={user.id}")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            has_profile=False
        )
    )


@router.post("/profile", response_model=dict)
@handle_app_errors
async def update_profile(
    profile_data: ProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新学生画像

    如果学生画像不存在则创建
    """
    logger.info(f"[Auth] Update profile for user: {current_user.id}")

    # 验证goal值
    valid_goals = ["考研", "考公", "就业", "出国", "未定", None]
    if profile_data.goal not in valid_goals:
        raise ValidationException(
            message="goal参数无效",
            details={"valid_values": ["考研", "考公", "就业", "出国", "未定"]}
        )

    # 验证grade值
    if profile_data.grade is not None and (profile_data.grade < 1 or profile_data.grade > 4):
        raise ValidationException(
            message="grade参数无效",
            details={"valid_values": [1, 2, 3, 4]}
        )

    # 查找或创建学生画像
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        # 创建新画像
        profile = StudentProfile(
            user_id=current_user.id,
            major=profile_data.major,
            grade=profile_data.grade,
            class_name=profile_data.class_name,
            goal=profile_data.goal
        )
        db.add(profile)
        logger.info(f"[Auth] Student profile created for user: {current_user.id}")
    else:
        # 更新画像
        if profile_data.major is not None:
            profile.major = profile_data.major
        if profile_data.grade is not None:
            profile.grade = profile_data.grade
        if profile_data.class_name is not None:
            profile.class_name = profile_data.class_name
        if profile_data.goal is not None:
            profile.goal = profile_data.goal
        logger.info(f"[Auth] Student profile updated for user: {current_user.id}")

    await db.commit()

    return {
        "success": True,
        "message": "资料完善成功"
    }


@router.get("/me", response_model=UserDetailResponse)
@handle_app_errors
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前登录用户完整信息
    """
    logger.info(f"[Auth] Get current user info: {current_user.id}")

    # 获取学生画像
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return UserDetailResponse(
        id=current_user.id,
        openid=current_user.openid,
        nickname=current_user.nickname,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        is_active=bool(current_user.is_active),
        last_login=current_user.last_login,
        has_profile=profile is not None,
        profile=StudentProfileResponse.model_validate(profile) if profile else None
    )
