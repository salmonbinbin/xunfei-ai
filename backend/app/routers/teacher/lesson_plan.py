"""
教师教案 API 路由
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas.lesson_plan import (
    LessonPlanCreateRequest,
    LessonPlanGenerateOutlineRequest,
    LessonPlanGeneratePptRequest,
    LessonPlanResponse,
    LessonPlanListResponse,
    PPTThemeListResponse,
    GenerateOutlineResponse,
    GeneratePptResponse,
    PptStatusResponse,
)
from app.services.lesson_plan_service import lesson_plan_service

logger = logging.getLogger("lesson_plan_api")
router = APIRouter(prefix="/api/teacher/lesson-plan", tags=["教师教案"])


@router.post("/", response_model=LessonPlanResponse)
async def create_lesson_plan(
    request: LessonPlanCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建教案（仅保存基本信息，不生成大纲/PPT）

    - title: 教案标题
    - course_name: 课程名称（可选）
    - knowledge_points: 知识点描述
    - target_audience: 授课对象（可选）
    - teaching_hours: 课时数（可选）
    - template_id: PPT模板ID（可选）
    """
    logger.info(f"[API] create_lesson_plan: title={request.title}")

    # TODO: 保存到数据库
    # 这里暂时返回模拟数据，后续需要创建数据库模型和保存逻辑
    from datetime import datetime
    from app.schemas.lesson_plan import LessonPlanStatus

    return LessonPlanResponse(
        id=1,
        title=request.title,
        course_name=request.course_name,
        outline=None,
        ppt_sid=None,
        ppt_url=None,
        template_id=request.template_id,
        status=LessonPlanStatus.DRAFT,
        error_msg=None,
        created_at=datetime.now()
    )


@router.get("/themes")
async def get_ppt_themes(
    style: Optional[str] = Query(None, description="风格"),
    color: Optional[str] = Query(None, description="颜色"),
    industry: Optional[str] = Query(None, description="行业"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量")
):
    """
    获取可选的PPT模板主题列表

    - style: 风格（简约/卡通/商务/创意/国风/清新/扁平/插画/节日）
    - color: 颜色（蓝色/绿色/红色/紫色/黑色/灰色/黄色/粉色/橙色）
    - industry: 行业（科技互联网/教育培训/政务/学院/电子商务/...）
    """
    logger.info(f"[API] get_ppt_themes: style={style}, color={color}, industry={industry}")

    try:
        result = await lesson_plan_service.get_ppt_themes(
            style=style,
            color=color,
            industry=industry,
            page=page,
            page_size=page_size
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"[API] get_ppt_themes failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-outline", response_model=GenerateOutlineResponse)
async def generate_outline(
    request: LessonPlanGenerateOutlineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成教学大纲（异步）

    - plan_id: 教案ID
    - knowledge_points: 更新的知识点（可选）
    """
    logger.info(f"[API] generate_outline: plan_id={request.plan_id}")

    try:
        # 构建prompt
        prompt = lesson_plan_service.build_lesson_plan_prompt(
            title="课程大纲",
            knowledge_points=request.knowledge_points or "课程内容",
        )

        # 异步生成大纲
        result = await lesson_plan_service.generate_outline(query=prompt)

        return GenerateOutlineResponse(
            success=True,
            sid=result["sid"],
            outline=result["outline"],
            message="大纲生成成功"
        )
    except Exception as e:
        logger.error(f"[API] generate_outline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-ppt", response_model=GeneratePptResponse)
async def generate_ppt(
    request: LessonPlanGeneratePptRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成PPT（异步，提交后返回sid，需轮询状态）

    - plan_id: 教案ID
    - template_id: 模板ID（可选）
    - is_ai_image: 是否AI配图
    - ai_image_type: AI配图类型（normal/advanced）
    - is_card_note: 是否生成演讲备注
    """
    logger.info(f"[API] generate_ppt: plan_id={request.plan_id}")

    try:
        # 调用PPT生成
        result = await lesson_plan_service.generate_ppt_by_outline(
            outline=request.outline,
            query="生成教学PPT",
            template_id=request.template_id,
            is_figure=request.is_ai_image,
            ai_image=request.ai_image_type,
            is_card_note=request.is_card_note
        )

        return GeneratePptResponse(
            success=True,
            sid=result["sid"],
            status="generating",
            message="PPT生成任务已提交"
        )
    except Exception as e:
        logger.error(f"[API] generate_ppt failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ppt-status/{sid}", response_model=PptStatusResponse)
async def get_ppt_status(sid: str, db: AsyncSession = Depends(get_db)):
    """
    查询PPT生成状态

    - sid: PPT任务ID（generate-ppt接口返回）
    """
    logger.info(f"[API] get_ppt_status: sid={sid}")

    try:
        result = await lesson_plan_service.poll_ppt_status(sid)
        return PptStatusResponse(
            success=True,
            **result
        )
    except Exception as e:
        logger.error(f"[API] get_ppt_status failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}", response_model=LessonPlanResponse)
async def get_lesson_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """获取教案详情"""
    logger.info(f"[API] get_lesson_plan: plan_id={plan_id}")

    from datetime import datetime
    from app.schemas.lesson_plan import LessonPlanStatus

    return LessonPlanResponse(
        id=plan_id,
        title="示例教案",
        course_name=None,
        outline=None,
        ppt_sid=None,
        ppt_url=None,
        template_id=None,
        status=LessonPlanStatus.DRAFT,
        error_msg=None,
        created_at=datetime.now()
    )


@router.get("/", response_model=LessonPlanListResponse)
async def list_lesson_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取教案列表"""
    logger.info(f"[API] list_lesson_plans: page={page}, page_size={page_size}")

    from datetime import datetime
    from app.schemas.lesson_plan import LessonPlanStatus

    return LessonPlanListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size
    )
