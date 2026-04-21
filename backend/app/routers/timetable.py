"""
课表路由

课程管理
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
import logging
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models.user import User, StudentProfile
from app.models.course import Course
from app.models.schedule import Schedule
from app.models.timetable import CourseAIInsight
from app.schemas.timetable import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    TodayCoursesResponse,
    ScheduleCreate,
    ScheduleResponse,
    TimetableImportRequest,
    TimetableImportResponse,
    CourseWithAIResponse,
    AIChatRequest,
    AIChatResponse
)
from sqlalchemy.orm import selectinload
from app.services.xinghuo_service import xinghuo_service
from app.services.ocr_service import ocr_service
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/timetable", tags=["课表"])


@router.get("", response_model=List[CourseResponse])
@handle_app_errors
async def get_courses(
    day_of_week: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的课程列表

    支持按星期几筛选
    """
    logger.info(f"[Timetable] Get courses for user {current_user.id}, day_of_week: {day_of_week}")

    # 构建查询
    query = select(Course).where(
        and_(
            Course.user_id == current_user.id,
            Course.is_deleted == False
        )
    )

    if day_of_week is not None:
        query = query.where(Course.day_of_week == day_of_week)

    query = query.offset(skip).limit(limit).order_by(Course.day_of_week, Course.start_slot)

    result = await db.execute(query)
    courses = result.scalars().all()

    logger.info(f"[Timetable] Found {len(courses)} courses")
    return courses


@router.get("/today", response_model=TodayCoursesResponse)
@handle_app_errors
async def get_today_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日课程和日程
    """
    logger.info(f"[Timetable] Get today courses for user {current_user.id}")

    # 计算今天是周几 (1=周一, 7=周日)
    today = datetime.now()
    day_of_week = today.isoweekday()
    date_str = today.strftime("%Y-%m-%d")

    # 查询今日课程
    courses_query = select(Course).where(
        and_(
            Course.user_id == current_user.id,
            Course.is_deleted == False,
            Course.day_of_week == day_of_week
        )
    ).order_by(Course.start_slot)

    courses_result = await db.execute(courses_query)
    courses = courses_result.scalars().all()

    # 查询今日日程
    schedules_query = select(Schedule).where(
        and_(
            Schedule.user_id == current_user.id,
            Schedule.is_deleted == False,
            Schedule.day_of_week == day_of_week
        )
    ).order_by(Schedule.time_desc)

    schedules_result = await db.execute(schedules_query)
    schedules = schedules_result.scalars().all()

    # 查询用户班别
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    student_profile = profile_result.scalar_one_or_none()
    class_name = student_profile.class_name if student_profile else None

    logger.info(f"[Timetable] Today ({date_str}, day {day_of_week}): {len(courses)} courses, {len(schedules)} schedules")

    return TodayCoursesResponse(
        date=date_str,
        day_of_week=day_of_week,
        class_name=class_name,
        courses=courses,
        schedules=schedules
    )


@router.post("", response_model=CourseResponse)
@handle_app_errors
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建课程
    """
    logger.info(f"[Timetable] Create course: {course_data.name} for user {current_user.id}")

    # 验证时间
    if course_data.start_slot > course_data.end_slot:
        raise ValidationException(
            message="开始节次不能大于结束节次",
            details={"start_slot": course_data.start_slot, "end_slot": course_data.end_slot}
        )

    # 创建课程记录
    course = Course(
        user_id=current_user.id,
        name=course_data.name,
        code=course_data.code,
        credit=course_data.credit,
        category=course_data.category,
        day_of_week=course_data.day_of_week,
        start_slot=course_data.start_slot,
        end_slot=course_data.end_slot,
        week_range=course_data.week_range,
        location=course_data.location,
        teacher=course_data.teacher,
        ai_tip=course_data.ai_tip,
        is_active=1
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    logger.info(f"[Timetable] Course created with id: {course.id}")
    return course


@router.put("/{course_id}", response_model=CourseResponse)
@handle_app_errors
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新课程
    """
    logger.info(f"[Timetable] Update course: {course_id} for user {current_user.id}")

    # 查询课程
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == course_id,
                Course.user_id == current_user.id,
                Course.is_deleted == False
            )
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise NotFoundException("Course", course_id)

    # 更新字段
    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)

    logger.info(f"[Timetable] Course {course_id} updated")
    return course


@router.delete("/{course_id}")
@handle_app_errors
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    软删除课程
    """
    logger.info(f"[Timetable] Delete course: {course_id} for user {current_user.id}")

    # 查询课程
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == course_id,
                Course.user_id == current_user.id,
                Course.is_deleted == False
            )
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise NotFoundException("Course", course_id)

    # 软删除
    course.is_deleted = True
    await db.commit()

    logger.info(f"[Timetable] Course {course_id} soft deleted")
    return {"message": "课程已删除"}


@router.post("/import/preview")
@handle_app_errors
async def import_timetable_preview(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    课表图片OCR识别预览
    使用星火图片理解API识别课表图片，然后用LLM解析为结构化数据
    """
    logger.info(f"[Timetable] Import preview for user {current_user.id}, file: {file.filename}")

    # 读取文件内容
    image_data = await file.read()
    logger.info(f"[Timetable] File size: {len(image_data)} bytes")

    # 调用星火图片理解服务
    try:
        result = await xinghuo_service.image_understanding(
            image_data=image_data,
            user_id=str(current_user.id),
            prompt="""你是一个专业的课表识别助手。请从课表图片中提取课程信息。

返回严格JSON格式（**只返回JSON，不要其他文字！**）：
{
  "courses": [
    {
      "name": "课程名称（纯净，不含其他信息）",
      "location": "如九教501、八教505、实训楼402，看不到写null",
      "day_of_week": 1-7数字（1=周一）,
      "start_slot": 1-12数字,
      "end_slot": 1-12数字,
      "week_range": "如1-16周、1-17周，看不到写null"
    }
  ]
}

**识别示例：**
- 图片文字"高等数学 九教501 1-2节 1-16周" → name:高等数学, location:九教501, day_of_week:1, start_slot:1, end_slot:2, week_range:1-16周
- 图片文字"大学英语 实训楼402 3-4节" → name:大学英语, location:实训楼402, day_of_week:2, start_slot:3, end_slot:4, week_range:null

**地点格式**：必须是"教学楼+数字"，如九教501、八教505、实训楼402。不是"教室501"也不是"501"。

**节次格式**：如"1-2节"、"3-4节"，对应start_slot=1, end_slot=2"""
        )
        logger.info(f"[Timetable] Image understanding result: {result}")

        # 记录识别结果详情
        courses = result.get("courses", [])
        logger.info(f"[Timetable] Parsed courses count: {len(courses)}")
        if courses:
            for i, c in enumerate(courses[:3]):  # 只打印前3门
                logger.info(f"[Timetable] Course {i+1}: name={c.get('name')}, teacher={c.get('teacher')}, location={c.get('location')}")

        # 检查是否返回了有效的courses
        courses = result.get("courses", [])
        if courses and len(courses) > 0:
            return {
                "success": True,
                "message": f"识别出{len(courses)}门课程",
                "raw_text": result.get("raw_text", ""),
                "courses": courses
            }

        # 如果没有courses，说明返回的是自然语言，用LLM解析
        raw_text = result.get("raw_text", "")
        if raw_text:
            logger.info(f"[Timetable] No courses in result, parsing raw text with LLM")
            parsed_courses = await xinghuo_service.parse_timetable(raw_text)
            return {
                "success": True,
                "message": f"识别出{len(parsed_courses)}门课程",
                "raw_text": raw_text,
                "courses": parsed_courses
            }

        # 没有任何结果
        return {
            "success": False,
            "message": "未能识别出课程信息，请上传清晰的课表图片",
            "raw_text": "",
            "courses": []
        }

    except Exception as e:
        logger.error(f"[Timetable] Image understanding failed: {e}", exc_info=True)
        raise ValidationException(
            message=f"课表识别失败: {str(e)}",
            details={"service": "XingHuo"}
        )


@router.post("/upload")
@handle_app_errors
async def upload_timetable(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传课表图片，使用讯飞OCR识别 + 星火大模型解析
    先用OCR提取文字，再用AI解析成结构化课程数据
    """
    logger.info(f"[Timetable] Upload timetable for user {current_user.id}, file: {file.filename}")

    # 读取文件内容
    image_data = await file.read()
    logger.info(f"[Timetable] File size: {len(image_data)} bytes")

    # 1. 调用OCR识别文字
    try:
        ocr_result = await ocr_service.recognize_document(image_data)
        raw_text = ocr_result.get("text", "")
        logger.info(f"[Timetable] OCR recognized text length: {len(raw_text)}")
    except Exception as e:
        logger.error(f"[Timetable] OCR failed: {e}", exc_info=True)
        raise ValidationException(
            message=f"OCR识别失败: {str(e)}",
            details={"service": "OCR"}
        )

    if not raw_text.strip():
        raise ValidationException(
            message="未能识别出文字，请上传清晰的课表图片",
            details={"service": "OCR"}
        )

    # 2. 调用星火大模型解析OCR结果
    try:
        parsed_courses = await xinghuo_service.parse_timetable(raw_text)
        logger.info(f"[Timetable] Parsed {len(parsed_courses)} courses")
    except Exception as e:
        logger.error(f"[Timetable] Parse failed: {e}", exc_info=True)
        raise ValidationException(
            message=f"课表解析失败: {str(e)}",
            details={"service": "XingHuo"}
        )

    return {
        "success": True,
        "message": f"成功识别并解析出{len(parsed_courses)}门课程",
        "raw_text": raw_text,
        "courses": parsed_courses
    }


@router.delete("/courses/clear")
@handle_app_errors
async def clear_all_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    清空用户的所有课程
    """
    logger.info(f"[Timetable] Clear all courses for user {current_user.id}")

    # 删除用户的所有课程
    result = await db.execute(
        delete(Course).where(Course.user_id == current_user.id)
    )
    await db.commit()

    deleted_count = result.rowcount
    logger.info(f"[Timetable] Deleted {deleted_count} courses")

    return {
        "success": True,
        "message": f"已清空 {deleted_count} 节课",
        "deleted_count": deleted_count
    }


@router.post("/import/confirm")
@handle_app_errors
async def import_timetable_confirm(
    import_data: TimetableImportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    确认导入课表到数据库
    """
    logger.info(f"[Timetable] Import confirm for user {current_user.id}, courses count: {len(import_data.courses)}, semester_start: {import_data.semester_start_date}")

    # 解析学期开始日期
    semester_start = None
    if import_data.semester_start_date:
        try:
            semester_start = datetime.strptime(import_data.semester_start_date, "%Y-%m-%d").date()
            logger.info(f"[Timetable] Semester start date: {semester_start}, weekday: {semester_start.isoweekday()}")
        except ValueError as e:
            logger.warning(f"[Timetable] Invalid semester start date: {import_data.semester_start_date}")

    created_count = 0
    errors = []

    for i, course_data in enumerate(import_data.courses):
        try:
            # 解析课程数据
            name = course_data.get("name")
            if not name:
                errors.append({"index": i, "error": "课程名称缺失"})
                continue

            # 清理课程名中的节次信息
            import re
            name = re.sub(r'\s*[\(（【\[【]?\d+[\-－]\d+\s*节?\s*[\)）】\]】]?\s*$', '', name).strip()

            # 获取时间信息
            day_of_week = course_data.get("day_of_week", 1)
            start_slot = course_data.get("start_slot", 1)
            end_slot = course_data.get("end_slot", start_slot)
            week_range = course_data.get("week_range", "1-16周")
            location = course_data.get("location")
            teacher = course_data.get("teacher")

            # 计算课程日期（根据学期开始日期和周几）
            course_date = None
            if semester_start and day_of_week:
                # 学期开始的周几
                start_weekday = semester_start.isoweekday()  # 1=周一, 7=周日
                # 计算目标周几相差的天数
                days_diff = day_of_week - start_weekday
                if days_diff < 0:
                    days_diff += 7
                # 计算第一周该课程的日期
                course_date = semester_start + timedelta(days=days_diff)
                logger.debug(f"[Timetable] day_of_week={day_of_week}, course_date={course_date}")

            # 创建课程
            course = Course(
                user_id=current_user.id,
                name=name,
                code=course_data.get("code"),
                credit=course_data.get("credit"),
                category=course_data.get("category"),
                day_of_week=day_of_week,
                start_slot=start_slot,
                end_slot=end_slot,
                week_range=week_range,
                location=location,
                teacher=teacher,
                ai_tip=None,
                is_active=1,
                course_date=course_date
            )
            db.add(course)
            created_count += 1
        except Exception as e:
            logger.error(f"[Timetable] Failed to import course {i}: {e}")
            errors.append({"index": i, "error": str(e)})

    await db.commit()
    logger.info(f"[Timetable] Imported {created_count} courses, errors: {len(errors)}")

    return {
        "message": f"成功导入 {created_count} 节课",
        "courses_count": created_count,
        "errors": errors if errors else None
    }


@router.get("/week", response_model=dict)
@handle_app_errors
async def get_week_timetable(
    week_offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取周课表

    Args:
        week_offset: 周偏移量（0=本周）
    """
    logger.info(f"[Timetable] Get week timetable for user {current_user.id}, offset: {week_offset}")

    # 计算目标周的日期范围
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)

    # 查询课程
    query = select(Course).where(
        and_(
            Course.user_id == current_user.id,
            Course.is_deleted == False
        )
    )
    result = await db.execute(query)
    courses = result.scalars().all()

    # 按周几分组
    week_courses = {day: [] for day in range(1, 8)}
    for course in courses:
        week_courses[course.day_of_week].append(CourseResponse.model_validate(course))

    return {
        "week_start": start_of_week.isoformat(),
        "week_offset": week_offset,
        "courses": week_courses
    }


@router.get("/courses/{course_id}", response_model=CourseWithAIResponse)
@handle_app_errors
async def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取课程详情（含AI建议）
    """
    logger.info(f"[Timetable] Get course detail: {course_id} for user {current_user.id}")

    # 查询课程
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == course_id,
                Course.user_id == current_user.id,
                Course.is_deleted == False
            )
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise NotFoundException("Course", course_id)

    # 获取AI洞察
    insight_result = await db.execute(
        select(CourseAIInsight).where(CourseAIInsight.course_id == course_id)
    )
    insight = insight_result.scalar_one_or_none()

    # 手动构建响应，避免懒加载问题
    response_data = {
        "id": course.id,
        "user_id": course.user_id,
        "name": course.name,
        "code": course.code,
        "credit": float(course.credit) if course.credit else None,
        "category": course.category,
        "day_of_week": course.day_of_week,
        "start_slot": course.start_slot,
        "end_slot": course.end_slot,
        "week_range": course.week_range,
        "location": course.location,
        "teacher": course.teacher,
        "ai_tip": course.ai_tip,
        "is_active": course.is_active,
        "created_at": course.created_at,
        "ai_insight": None
    }

    if insight:
        from app.schemas.timetable import AIInsightResponse
        response_data["ai_insight"] = AIInsightResponse.model_validate(insight)

    return CourseWithAIResponse(**response_data)


@router.post("/ai-insights/{course_id}")
@handle_app_errors
async def generate_ai_insights(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    为课程生成AI学习建议
    """
    logger.info(f"[Timetable] Generate AI insights for course {course_id} user {current_user.id}")

    # 查询课程
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == course_id,
                Course.user_id == current_user.id,
                Course.is_deleted == False
            )
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise NotFoundException("Course", course_id)

    # 调用星火大模型生成建议
    course_info = {
        "name": course.name,
        "category": course.category or "专业",
        "credit": str(course.credit) if course.credit else "未知"
    }

    insight_data = await xinghuo_service.generate_course_insight(course_info)

    # 更新或创建AI洞察记录
    insight_result = await db.execute(
        select(CourseAIInsight).where(CourseAIInsight.course_id == course_id)
    )
    existing_insight = insight_result.scalar_one_or_none()

    if existing_insight:
        existing_insight.course_summary = insight_data.get("course_summary")
        existing_insight.learning_tips = insight_data.get("learning_tips")
        existing_insight.preview_suggestion = insight_data.get("preview_suggestion")
        existing_insight.review_suggestion = insight_data.get("review_suggestion")
        existing_insight.key_points = insight_data.get("key_points")
        existing_insight.difficulty_level = insight_data.get("difficulty_level")
        existing_insight.importance = insight_data.get("importance")
    else:
        new_insight = CourseAIInsight(
            course_id=course_id,
            course_summary=insight_data.get("course_summary"),
            learning_tips=insight_data.get("learning_tips"),
            preview_suggestion=insight_data.get("preview_suggestion"),
            review_suggestion=insight_data.get("review_suggestion"),
            key_points=insight_data.get("key_points"),
            difficulty_level=insight_data.get("difficulty_level"),
            importance=insight_data.get("importance")
        )
        db.add(new_insight)

    await db.commit()

    logger.info(f"[Timetable] AI insights generated for course {course_id}")
    return {"success": True, "message": "AI学习建议已生成", "insight": insight_data}


@router.post("/ai-chat", response_model=AIChatResponse)
@handle_app_errors
async def ai_chat_about_course(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI学伴问答
    """
    logger.info(f"[Timetable] AI chat for course {request.course_id} user {current_user.id}")

    # 查询课程
    result = await db.execute(
        select(Course).where(
            and_(
                Course.id == request.course_id,
                Course.user_id == current_user.id,
                Course.is_deleted == False
            )
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise NotFoundException("Course", request.course_id)

    course_info = {
        "name": course.name,
        "category": course.category,
        "teacher": course.teacher
    }

    answer = await xinghuo_service.chat_about_course(
        request.course_id,
        request.question,
        course_info
    )

    return AIChatResponse(answer=answer, course_id=request.course_id)

