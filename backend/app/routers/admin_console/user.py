"""
用户管理路由
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from jose import jwt

from app.database import get_db
from app.models import User, AdminLog
from app.utils.errors import handle_app_errors
from app.config import settings

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/admin/users", tags=["管理端-用户管理"])


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
        logger.error(f"[Users] Token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")


class StatusUpdateRequest(BaseModel):
    status: str
    reason: Optional[str] = None


@router.get("")
@handle_app_errors
async def get_users(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    role: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Users] Get users, admin_id={admin_id}, page={page}, role={role}, status={status}, keyword={keyword}")

    try:
        # 构建查询条件
        conditions = [User.is_deleted == 0]
        if role:
            conditions.append(User.role == role)
        if status:
            conditions.append(User.status == status)
        if keyword:
            conditions.append(
                (User.nickname.ilike(f"%{keyword}%")) | (User.phone.ilike(f"%{keyword}%"))
            )

        # 获取总数
        result = await db.execute(
            select(func.count(User.id)).where(*conditions)
        )
        total = result.scalar() or 0

        # 获取分页数据
        offset = (page - 1) * page_size
        query = (
            select(User)
            .where(*conditions)
            .order_by(User.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await db.execute(query)
        users = result.scalars().all()

        items = []
        for user in users:
            # 获取用户对话次数
            from app.models import Conversation
            result2 = await db.execute(
                select(func.count(Conversation.id)).where(Conversation.user_id == user.id)
            )
            chat_count = result2.scalar() or 0

            # 手机号脱敏
            phone = user.phone or ""
            if len(phone) >= 7:
                phone = phone[:3] + "****" + phone[-4:]

            # 获取专业/院系
            major = None
            department = None
            if user.role == "student":
                from app.models import StudentProfile
                result_prof = await db.execute(
                    select(StudentProfile.major).where(StudentProfile.user_id == user.id)
                )
                major = result_prof.scalar_one_or_none()
            elif user.role == "teacher":
                from app.models import TeacherProfile
                result_prof = await db.execute(
                    select(TeacherProfile.department).where(TeacherProfile.user_id == user.id)
                )
                department = result_prof.scalar_one_or_none()

            items.append({
                "id": user.id,
                "nickname": user.nickname or "未设置",
                "phone": phone,
                "role": user.role,
                "major": major,
                "department": department,
                "status": user.status or "active",
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "total_chats": chat_count,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })

        logger.info(f"[Users] Fetched {len(items)} users, total={total}")

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
        logger.error(f"[Users] Error fetching users: {e}", exc_info=True)
        return {
            "success": True,
            "data": {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        }


@router.get("/{user_id}")
@handle_app_errors
async def get_user_detail(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Users] Get user detail, user_id={user_id}, admin_id={admin_id}")

    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == 0))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 获取额外统计
    from app.models import Conversation, ReviewRecord, TranslationTask
    result2 = await db.execute(select(func.count(Conversation.id)).where(Conversation.user_id == user_id))
    chat_count = result2.scalar() or 0

    result3 = await db.execute(select(func.count(ReviewRecord.id)).where(ReviewRecord.user_id == user_id))
    recording_count = result3.scalar() or 0

    result4 = await db.execute(select(func.count(TranslationTask.id)).where(TranslationTask.user_id == user_id))
    translation_count = result4.scalar() or 0

    return {
        "success": True,
        "data": {
            "id": user.id,
            "nickname": user.nickname,
            "phone": user.phone,
            "role": user.role,
            "status": user.status,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "total_chats": chat_count,
            "total_recordings": recording_count,
            "total_translations": translation_count,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.post("/{user_id}/status")
@handle_app_errors
async def update_user_status(
    request: Request,
    user_id: int,
    body: StatusUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """修改用户状态"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Users] Update user {user_id} status to {body.status}, admin_id={admin_id}")

    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == 0))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 更新状态
    await db.execute(
        update(User).where(User.id == user_id).values(status=body.status, updated_at=datetime.now())
    )
    await db.commit()

    # 记录操作日志
    log = AdminLog(
        admin_id=admin_id,
        admin_name="管理员",
        action="user.status",
        action_text="修改用户状态" if body.status == "active" else "禁用用户",
        target_type="user",
        target_id=user_id,
        detail={"status": body.status, "reason": body.reason},
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    await db.commit()

    status_text = "已启用" if body.status == "active" else "已禁用"
    logger.info(f"[Users] User {user_id} status updated to {body.status}")

    return {
        "success": True,
        "message": f"用户{status_text}"
    }


@router.get("/export")
@handle_app_errors
async def export_users(
    request: Request,
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """导出用户Excel"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Users] Export users, admin_id={admin_id}")

    # 构建查询条件
    conditions = [User.is_deleted == 0]
    if role:
        conditions.append(User.role == role)
    if status:
        conditions.append(User.status == status)

    result = await db.execute(
        select(User).where(*conditions).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    # 生成Excel
    from io import BytesIO
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "用户列表"

    # 表头
    headers = ["ID", "昵称", "手机号", "角色", "专业/院系", "状态", "注册时间", "最后登录"]
    ws.append(headers)

    # 数据
    for user in users:
        # 获取专业/院系
        major = None
        department = None
        if user.role == "student":
            from app.models import StudentProfile
            result_prof = await db.execute(
                select(StudentProfile.major).where(StudentProfile.user_id == user.id)
            )
            major = result_prof.scalar_one_or_none()
        elif user.role == "teacher":
            from app.models import TeacherProfile
            result_prof = await db.execute(
                select(TeacherProfile.department).where(TeacherProfile.user_id == user.id)
            )
            department = result_prof.scalar_one_or_none()

        ws.append([
            user.id,
            user.nickname or "未设置",
            user.phone or "",
            "学生" if user.role == "student" else "教师",
            major if user.role == "student" else department or "-",
            "正常" if user.status == "active" else "已禁用",
            user.created_at.isoformat() if user.created_at else "",
            user.last_login.isoformat() if user.last_login else ""
        ])

    # 保存
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    from fastapi.responses import StreamingResponse
    import datetime

    filename = f"AI小商用户列表_{datetime.date.today().isoformat()}.xlsx"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )