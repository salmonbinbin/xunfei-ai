"""
教师认证路由

教师注册、登录、JWT Token管理
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import asyncio

from app.database import get_db
from app.models.user import User, UserRole
from app.models.teacher_profile import TeacherProfile
from app.schemas.teacher import (
    TeacherRegisterRequest,
    TeacherLoginRequest,
    TeacherLoginResponse,
    TeacherResponse,
)
from app.utils.auth import create_access_token, get_current_teacher, get_password_hash, verify_password
from app.utils.errors import handle_app_errors, ValidationException
from app.services.login_log_service import save_login_log

logger = logging.getLogger("teacher-auth")

router = APIRouter(prefix="/api/auth/teacher", tags=["教师认证"])


@router.post("/register")
@handle_app_errors
async def register(register_data: TeacherRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    教师注册

    1. 检查手机号是否已存在
    2. 创建新用户（密码加密存储，role=teacher）
    3. 创建教师画像
    4. 生成JWT token返回
    """
    logger.info(f"[TeacherAuth] Register attempt for phone: {register_data.phone}")

    try:
        # 检查手机号是否已存在
        result = await db.execute(select(User).where(User.phone == register_data.phone))
        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            logger.warning(f"[TeacherAuth] Register failed - phone already exists: {register_data.phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已注册，请直接登录"
            )

        logger.info(f"[TeacherAuth] Phone check passed, creating user...")

        # 密码哈希
        password_hash = get_password_hash(register_data.password)
        logger.info(f"[TeacherAuth] Password hashed successfully")

        # 创建新用户（role为teacher）
        user = User(
            phone=register_data.phone,
            password_hash=password_hash,
            nickname=register_data.name,
            status="active",
            role=UserRole.teacher
        )
        logger.info(f"[TeacherAuth] User object created, role={UserRole.teacher}")

        db.add(user)
        await db.flush()  # 获取user.id
        logger.info(f"[TeacherAuth] User flushed to DB, id={user.id}")

        # 创建教师画像
        teacher_profile = TeacherProfile(
            user_id=user.id,
            department=register_data.department,
            title=register_data.title
        )
        logger.info(f"[TeacherAuth] TeacherProfile object created")

        db.add(teacher_profile)
        await db.flush()
        logger.info(f"[TeacherAuth] TeacherProfile flushed to DB, profile_id={teacher_profile.id}")

        await db.commit()
        logger.info(f"[TeacherAuth] Commit successful")

        await db.refresh(user)
        logger.info(f"[TeacherAuth] User refreshed, id={user.id}, role={user.role}")

        # 生成JWT token（包含role=teacher）
        access_token = create_access_token(user_id=user.id, role="teacher")
        logger.info(f"[TeacherAuth] Token generated successfully")

        logger.info(f"[TeacherAuth] Teacher registered successfully: id={user.id}, phone={register_data.phone}")

        # 记录登录日志（异步，不阻塞响应）
        try:
            asyncio.create_task(save_login_log(
                user_id=user.id,
                user_type="teacher",
                login_method="phone"
            ))
        except Exception as log_err:
            logger.warning(f"[TeacherAuth] Failed to save login log: {log_err}")

        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "role": "teacher",
                "teacher": TeacherResponse(
                    id=user.id,
                    phone=user.phone,
                    name=user.nickname or register_data.name,
                    department=register_data.department,
                    title=register_data.title
                )
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TeacherAuth] Register failed with exception: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login")
@handle_app_errors
async def login(login_data: TeacherLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    教师登录（账号密码）

    1. 使用手机号查找用户
    2. 验证密码
    3. 验证角色为教师
    4. 生成JWT token返回（包含role=teacher）
    """
    logger.info(f"[TeacherAuth] Login attempt for phone: {login_data.phone}")

    # 使用手机号查找用户
    result = await db.execute(select(User).where(User.phone == login_data.phone))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(f"[TeacherAuth] Login failed - user not found: {login_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"[TeacherAuth] Login failed - wrong password for phone: {login_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户是否被禁用
    if user.status == "disabled":
        logger.warning(f"[TeacherAuth] Login failed - user disabled: {login_data.phone}")
        disable_msg = "账号已被禁用"
        if user.disable_reason:
            disable_msg += f"，原因：{user.disable_reason}"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=disable_msg
        )

    # 验证角色为教师
    if user.role != UserRole.teacher:
        logger.warning(f"[TeacherAuth] Login failed - user is not teacher: {login_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号不是教师账号"
        )

    # 更新最后登录时间（使用本地时间，避免时区问题）
    user.last_login = datetime.now()
    await db.commit()
    await db.refresh(user)

    # 获取教师画像
    profile_result = await db.execute(
        select(TeacherProfile).where(TeacherProfile.user_id == user.id)
    )
    teacher_profile = profile_result.scalar_one_or_none()

    # 生成JWT token（包含role=teacher）
    access_token = create_access_token(user_id=user.id, role="teacher")

    logger.info(f"[TeacherAuth] Teacher logged in successfully: id={user.id}, phone={login_data.phone}")

    # 记录登录日志（异步，不阻塞响应）
    try:
        asyncio.create_task(save_login_log(
            user_id=user.id,
            user_type="teacher",
            login_method="phone"
        ))
    except Exception as log_err:
        logger.warning(f"[TeacherAuth] Failed to save login log: {log_err}")

    return {
        "success": True,
        "data": TeacherLoginResponse(
            access_token=access_token,
            token_type="bearer",
            role="teacher",
            teacher=TeacherResponse(
                id=user.id,
                phone=user.phone,
                name=user.nickname or "",
                department=teacher_profile.department if teacher_profile else None,
                title=teacher_profile.title if teacher_profile else None
            )
        )
    }


@router.get("/profile")
@handle_app_errors
async def get_teacher_profile(
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前教师用户信息

    需要教师权限
    """
    logger.info(f"[TeacherAuth] Get teacher profile: user_id={current_user.id}")

    # 获取教师画像
    profile_result = await db.execute(
        select(TeacherProfile).where(TeacherProfile.user_id == current_user.id)
    )
    teacher_profile = profile_result.scalar_one_or_none()

    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "phone": current_user.phone,
            "name": current_user.nickname,
            "department": teacher_profile.department if teacher_profile else None,
            "office": teacher_profile.office if teacher_profile else None,
            "title": teacher_profile.title if teacher_profile else None
        }
    }
