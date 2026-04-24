"""
智能选课助手路由

学生画像、智能推荐、时间冲突检测、对话咨询
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
import logging

from app.models.user import User
from app.schemas.course_advisor import (
    ProfileResponse,
    RecommendRequest,
    RecommendResponse,
    CourseDetailResponse,
    ChatRequest,
    ChatResponse,
    ConfirmRequest,
    ConfirmResponse,
)
from app.services.course_advisor_service import course_advisor_service
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("course_advisor")

router = APIRouter(prefix="/api/course-advisor", tags=["智能选课助手"])


# ============ 获取学生画像 ============

@router.get("/profile", response_model=ProfileResponse)
@handle_app_errors
async def get_student_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取学生画像

    返回学生的学习力雷达图、能力偏向、目标匹配度等信息
    """
    logger.info(f"[CourseAdvisor] Get profile - user: {current_user.id}")

    profile = await course_advisor_service.get_student_profile(db, current_user.id)

    return ProfileResponse(
        success=True,
        major=profile["major"],
        grade=profile["grade"],
        goal=profile["goal"],
        gpa=profile["gpa"],
        completed_credits=profile["completed_credits"],
        required_credits=profile["required_credits"],
        radar_data=profile["radar_data"],
        ability_type=profile["ability_type"],
        ai_suggestion=profile["ai_suggestion"]
    )


# ============ 获取AI推荐 ============

@router.post("/recommend", response_model=RecommendResponse)
@handle_app_errors
async def get_course_recommendations(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取AI推荐课程

    基于学生画像、目标、难度梯度等进行智能推荐
    - 支持按类别筛选：all/mandatory/elective/cross_major
    - 支持按目标筛选：考研/考公/就业/出国
    """
    logger.info(
        f"[CourseAdvisor] Get recommendations - user: {current_user.id}, "
        f"semester: {request.semester}, category: {request.category}"
    )

    result = await course_advisor_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        semester=request.semester,
        category=request.category,
        goal_filter=request.goal_filter,
        page=request.page,
        page_size=request.page_size
    )

    return RecommendResponse(
        success=True,
        courses=result["courses"],
        total_credits=result["total_credits"],
        message=result["message"],
        total=result.get("total", 0),
        page=result.get("page", 1),
        page_size=result.get("page_size", 5),
        total_pages=result.get("total_pages", 0)
    )


# ============ 获取课程详情 ============

@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
@handle_app_errors
async def get_course_detail(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取课程详情

    返回课程的完整信息、先修课程、替代课程、热门搭配
    """
    logger.info(f"[CourseAdvisor] Get course detail - user: {current_user.id}, course: {course_id}")

    result = await course_advisor_service.get_course_detail(db, course_id, current_user.id)

    return CourseDetailResponse(
        success=True,
        course=result["course"],
        prerequisites=result.get("prerequisites", []),
        alternatives=result.get("alternatives", []),
        popular_combinations=result.get("popular_combinations", [])
    )


# ============ 对话咨询 ============

@router.post("/chat", response_model=ChatResponse)
@handle_app_errors
async def chat_consultation(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    对话咨询

    自然语言查询选课建议，如"我想选一门对考研有帮助的数学课"
    """
    logger.info(f"[CourseAdvisor] Chat - user: {current_user.id}, message: {request.message[:50]}, history length: {len(request.history) if request.history else 0}")

    # 调试：打印接收到的请求数据
    logger.debug(f"[CourseAdvisor] ChatRequest received: message={request.message}, history={request.history}")

    result = await course_advisor_service.chat_consultation(
        user_id=current_user.id,
        message=request.message,
        history=request.history,
        db=db
    )

    return ChatResponse(
        success=True,
        reply=result["reply"],
        recommended_courses=result.get("recommended_courses"),
        suggestions=result.get("suggestions")
    )


# ============ 确认选课方案 ============

@router.post("/confirm", response_model=ConfirmResponse)
@handle_app_errors
async def confirm_selection(
    request: ConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    确认选课方案

    保存学生选择的课程方案，检测时间冲突
    """
    logger.info(
        f"[CourseAdvisor] Confirm selection - user: {current_user.id}, "
        f"semester: {request.semester}, courses: {request.selected_courses}"
    )

    result = await course_advisor_service.confirm_selection(
        db=db,
        user_id=current_user.id,
        semester=request.semester,
        selected_course_ids=request.selected_courses
    )

    return ConfirmResponse(
        success=True,
        plan_id=result["plan_id"],
        message=result["message"],
        conflicts=result.get("conflicts", []),
        total_credits=result["total_credits"]
    )


# ============ 获取我的已选课程 ============

@router.get("/my-courses")
@handle_app_errors
async def get_my_selected_courses(
    semester: str = "2024-1",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我在当前学期已选的课程

    从课表中获取已保存的选课方案
    """
    logger.info(f"[CourseAdvisor] Get my courses - user: {current_user.id}, semester: {semester}")

    result = await course_advisor_service.get_my_selected_courses(db, current_user.id)

    return {
        "success": True,
        "courses": result["courses"],
        "total_credits": result.get("total_credits", 0)
    }


# ============ 根据名称搜索课程 ============

@router.get("/course/search")
@handle_app_errors
async def search_course_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据课程名称搜索课程目录

    用于AI对话推荐课程时获取完整课程信息
    """
    logger.info(f"[CourseAdvisor] Search course by name: {name}")

    course = await course_advisor_service.search_course_by_name(db, name)

    if course:
        return {
            "success": True,
            "course": course
        }
    else:
        return {
            "success": False,
            "error": "课程不存在"
        }