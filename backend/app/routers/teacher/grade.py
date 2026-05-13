"""
成绩管理路由

成绩上传、查询、统计、AI分析报告生成
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.grade import GradeRecord, GradeItem
from app.schemas.grade import (
    GradeUploadResponse,
    GradeRecordListResponse,
    GradeRecordListItem,
    GradeRecordDetailResponse,
    GradeItemResponse,
    GradeStatsResponse,
    GradeBasicStats,
    GradeDistributionItem,
    GradeComponentStats,
    AIReportResponse,
    ExamAnalysis,
    GradeDeleteResponse,
)
from app.services.grade_service import grade_service
from app.utils.auth import get_current_teacher
from app.utils.errors import handle_app_errors, ValidationException

logger = logging.getLogger("teacher-grade")

router = APIRouter(prefix="/api/teacher/grade", tags=["成绩管理"])


@router.post("/upload")
@handle_app_errors
async def upload_grade(
    file: UploadFile = File(..., description="成绩Excel文件"),
    course_name: str = Form(..., description="课程名称"),
    semester: Optional[str] = Form(None, description="学期"),
    class_name: Optional[str] = Form(None, description="班级名称"),
    weights_json: Optional[str] = Form(None, description="权重JSON字符串"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    上传成绩Excel

    1. 解析Excel文件
    2. 计算总评和排名
    3. 保存到数据库
    4. 返回统计信息
    """
    logger.info(f"[Grade] Upload started by teacher {current_user.id}, course: {course_name}")
    logger.info(f"[Grade] File: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
    logger.info(f"[Grade] All form fields received successfully")

    # 检查文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise ValidationException(
            message="文件格式不正确",
            details={"hint": "请上传 .xlsx 或 .xls 格式的Excel文件"}
        )

    # 检查文件大小（5MB）
    file_size = 0
    file_content = b""
    while chunk := await file.read(1024 * 1024):  # 1MB chunks
        file_size += len(chunk)
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationException(
                message="文件过大",
                details={"hint": "文件大小不能超过5MB"}
            )
        file_content += chunk

    # 解析权重
    import json
    weights = {"usual": 0.4, "midterm": 0.2, "final": 0.4, "practice": 0.0}
    if weights_json:
        try:
            weights = json.loads(weights_json)
        except json.JSONDecodeError:
            pass  # 使用默认权重

    # 解析Excel
    items = await grade_service.parse_excel(file_content, weights)
    if not items:
        raise ValidationException(
            message="成绩表为空",
            details={"hint": "请确保Excel包含学生成绩数据"}
        )

    # 计算排名
    items = await grade_service.calculate_grades(items, weights)

    # 计算统计
    stats = await grade_service.calculate_stats(items)

    # 保存到数据库
    try:
        # 创建成绩记录
        record = GradeRecord(
            teacher_id=current_user.id,
            course_name=course_name,
            semester=semester,
            class_name=class_name,
            weights=weights,
            stats_data=stats
        )
        db.add(record)
        await db.flush()
        logger.info(f"[Grade] Record created: id={record.id}")

        # 创建成绩明细
        for item in items:
            grade_item = GradeItem(
                record_id=record.id,
                student_name=item["student_name"],
                student_no=item.get("student_no"),
                usual_score=item.get("usual_score"),
                midterm_score=item.get("midterm_score"),
                final_score=item.get("final_score"),
                practice_score=item.get("practice_score"),
                total_score=item.get("total_score"),
                ranking=item.get("rank"),
                status=item.get("status", "normal")
            )
            db.add(grade_item)

        await db.commit()
        logger.info(f"[Grade] Saved {len(items)} grade items")

    except Exception as e:
        await db.rollback()
        logger.error(f"[Grade] Save failed: {str(e)}", exc_info=True)
        raise

    basic = stats["basic"]

    return {
        "success": True,
        "data": GradeUploadResponse(
            record_id=record.id,
            course_name=course_name,
            item_count=len(items),
            stats=GradeBasicStats(
                total_students=basic["total_students"],
                avg_score=basic["avg_score"],
                pass_rate=basic["pass_rate"],
                max_score=basic["max_score"],
                min_score=basic["min_score"]
            )
        )
    }


@router.get("/records")
@handle_app_errors
async def get_grade_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    获取成绩记录列表
    """
    logger.info(f"[Grade] Get records by teacher {current_user.id}, page={page}")

    # 查询记录
    query = (
        select(GradeRecord)
        .where(GradeRecord.teacher_id == current_user.id)
        .where(GradeRecord.is_deleted == False)
        .order_by(desc(GradeRecord.created_at))
    )

    # 获取总数
    count_query = select(func.count()).where(
        GradeRecord.teacher_id == current_user.id,
        GradeRecord.is_deleted == False
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    # 获取每个记录的学生数量和统计
    record_items = []
    for record in records:
        # 查询该记录的学生数量
        count_q = select(func.count()).where(
            GradeItem.record_id == record.id,
            GradeItem.is_deleted == False
        )
        count_result = await db.execute(count_q)
        student_count = count_result.scalar()

        stats = record.stats_data or {}
        basic = stats.get("basic", {})

        record_items.append(GradeRecordListItem(
            id=record.id,
            course_name=record.course_name,
            class_name=record.class_name,
            semester=record.semester,
            student_count=student_count,
            avg_score=basic.get("avg_score"),
            pass_rate=basic.get("pass_rate"),
            created_at=record.created_at
        ))

    return {
        "success": True,
        "data": {
            "records": [r.model_dump() for r in record_items],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/records/{record_id}")
@handle_app_errors
async def get_grade_detail(
    record_id: int,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    获取成绩详情（含明细和统计）
    """
    logger.info(f"[Grade] Get detail by teacher {current_user.id}, record_id={record_id}")

    # 查询记录
    query = select(GradeRecord).where(
        GradeRecord.id == record_id,
        GradeRecord.teacher_id == current_user.id,
        GradeRecord.is_deleted == False
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    # 查询明细
    items_query = (
        select(GradeItem)
        .where(GradeItem.record_id == record_id)
        .where(GradeItem.is_deleted == False)
        .order_by(GradeItem.ranking)
    )
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    # 转换为响应模型
    item_responses = [
        GradeItemResponse(
            id=item.id,
            student_name=item.student_name,
            student_no=item.student_no,
            usual_score=float(item.usual_score) if item.usual_score else None,
            midterm_score=float(item.midterm_score) if item.midterm_score else None,
            final_score=float(item.final_score) if item.final_score else None,
            practice_score=float(item.practice_score) if item.practice_score else None,
            total_score=float(item.total_score) if item.total_score else None,
            rank=item.ranking,
            status=item.status.value if hasattr(item.status, 'value') else item.status
        )
        for item in items
    ]

    stats = record.stats_data or {}
    basic = stats.get("basic", {})
    distribution = stats.get("distribution", [])
    by_component = stats.get("by_component", {})

    # 转换by_component
    component_stats = {}
    for comp_name, comp_data in by_component.items():
        component_stats[comp_name] = GradeComponentStats(
            avg=comp_data.get("avg", 0),
            max=comp_data.get("max", 0),
            min=comp_data.get("min", 0)
        )

    stats_response = GradeStatsResponse(
        basic=GradeBasicStats(
            total_students=basic.get("total_students", 0),
            avg_score=basic.get("avg_score", 0),
            pass_rate=basic.get("pass_rate", 0),
            max_score=basic.get("max_score", 0),
            min_score=basic.get("min_score", 0)
        ),
        distribution=[
            GradeDistributionItem(range=d["range"], count=d["count"])
            for d in distribution
        ],
        by_component=component_stats or None
    )

    return {
        "success": True,
        "data": {
            "id": record.id,
            "course_name": record.course_name,
            "class_name": record.class_name,
            "semester": record.semester,
            "weights": record.weights or {"usual": 0.4, "midterm": 0.2, "final": 0.4, "practice": 0.0},
            "items": [item.model_dump() for item in item_responses],
            "stats": stats_response.model_dump()
        }
    }


@router.get("/records/{record_id}/report")
@handle_app_errors
async def get_ai_report(
    record_id: int,
    regenerate: bool = Query(False, description="是否重新生成"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    获取AI分析报告

    如果已有报告且regenerate=False，直接返回缓存
    """
    logger.info(f"[Grade] Get report by teacher {current_user.id}, record_id={record_id}, regenerate={regenerate}")

    # 查询记录
    query = select(GradeRecord).where(
        GradeRecord.id == record_id,
        GradeRecord.teacher_id == current_user.id,
        GradeRecord.is_deleted == False
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    # 如果有缓存报告且不需要重新生成
    if record.ai_report and not regenerate:
        import json
        try:
            report_data = json.loads(record.ai_report)
            suggestions = report_data.get("suggestions", "")
            if isinstance(suggestions, list):
                suggestions = "\n\n".join(suggestions)
            return {
                "success": True,
                "data": AIReportResponse(
                    course_name=record.course_name,
                    semester=record.semester,
                    summary=report_data.get("summary", ""),
                    high_performers=report_data.get("high_performers", []),
                    needs_attention=report_data.get("needs_attention", []),
                    exam_analysis=ExamAnalysis(
                        difficulty=report_data.get("exam_analysis", {}).get("difficulty", 0.5),
                        difficulty_text=report_data.get("exam_analysis", {}).get("difficulty_text", "适中"),
                        discrimination=report_data.get("exam_analysis", {}).get("discrimination", 0.3),
                        discrimination_text=report_data.get("exam_analysis", {}).get("discrimination_text", "良好")
                    ),
                    suggestions=suggestions
                )
            }
        except json.JSONDecodeError:
            pass

    # 查询明细
    items_query = (
        select(GradeItem)
        .where(GradeItem.record_id == record_id)
        .where(GradeItem.is_deleted == False)
        .order_by(GradeItem.ranking)
    )
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    # 转换为字典
    items_dict = [
        {
            "student_name": item.student_name,
            "student_no": item.student_no,
            "usual_score": float(item.usual_score) if item.usual_score is not None else None,
            "midterm_score": float(item.midterm_score) if item.midterm_score is not None else None,
            "final_score": float(item.final_score) if item.final_score is not None else None,
            "practice_score": float(item.practice_score) if item.practice_score is not None else None,
            "total_score": float(item.total_score) if item.total_score is not None else None,
            "rank": item.ranking,
            "status": item.status.value if hasattr(item.status, 'value') else item.status
        }
        for item in items
    ]

    # 获取统计
    stats = record.stats_data or {}
    if not stats:
        stats = await grade_service.calculate_stats(items_dict)

    # 生成AI报告
    report = await grade_service.generate_ai_report(
        course_name=record.course_name,
        semester=record.semester,
        items=items_dict,
        stats=stats
    )

    # 缓存报告
    import json
    record.ai_report = json.dumps(report, ensure_ascii=False)
    await db.commit()

    return {
        "success": True,
        "data": AIReportResponse(
            course_name=report["course_name"],
            semester=report["semester"],
            summary=report["summary"],
            high_performers=report["high_performers"],
            needs_attention=report["needs_attention"],
            exam_analysis=ExamAnalysis(
                difficulty=report["exam_analysis"]["difficulty"],
                difficulty_text=report["exam_analysis"]["difficulty_text"],
                discrimination=report["exam_analysis"]["discrimination"],
                discrimination_text=report["exam_analysis"]["discrimination_text"]
            ),
            suggestions=report["suggestions"]
        )
    }


@router.delete("/records/{record_id}")
@handle_app_errors
async def delete_grade_record(
    record_id: int,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    删除成绩记录（软删除）
    """
    logger.info(f"[Grade] Delete by teacher {current_user.id}, record_id={record_id}")

    # 查询记录
    query = select(GradeRecord).where(
        GradeRecord.id == record_id,
        GradeRecord.teacher_id == current_user.id,
        GradeRecord.is_deleted == False
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    # 软删除
    record.is_deleted = True
    await db.commit()

    return {
        "success": True,
        "data": GradeDeleteResponse(success=True, message="删除成功")
    }


@router.get("/records/{record_id}/export")
@handle_app_errors
async def export_grade(
    record_id: int,
    sort_by: Optional[str] = Query(None, description="排序字段 (total_score, usual_score, midterm_score, final_score, practice_score, student_name, rank)"),
    sort_order: Optional[str] = Query("descending", description="排序顺序 (ascending, descending)"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db)
):
    """
    导出成绩Excel

    支持自定义排序，默认按排名导出
    """
    logger.info(f"[Grade] Export by teacher {current_user.id}, record_id={record_id}, sort_by={sort_by}, sort_order={sort_order}")

    # 查询记录
    query = select(GradeRecord).where(
        GradeRecord.id == record_id,
        GradeRecord.teacher_id == current_user.id,
        GradeRecord.is_deleted == False
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    # 排序字段映射
    sort_field_mapping = {
        "total_score": GradeItem.total_score,
        "usual_score": GradeItem.usual_score,
        "midterm_score": GradeItem.midterm_score,
        "final_score": GradeItem.final_score,
        "practice_score": GradeItem.practice_score,
        "student_name": GradeItem.student_name,
        "rank": GradeItem.ranking,
    }

    # 构建排序
    order_column = GradeItem.ranking  # 默认排序
    if sort_by and sort_by in sort_field_mapping:
        order_column = sort_field_mapping[sort_by]
        if sort_order == "ascending":
            order_column = asc(order_column)
        else:
            order_column = desc(order_column)

    # 查询明细
    items_query = (
        select(GradeItem)
        .where(GradeItem.record_id == record_id)
        .where(GradeItem.is_deleted == False)
        .order_by(order_column)
    )
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    # 转换为字典
    items_dict = [
        {
            "student_name": item.student_name,
            "student_no": item.student_no,
            "usual_score": float(item.usual_score) if item.usual_score is not None else None,
            "midterm_score": float(item.midterm_score) if item.midterm_score is not None else None,
            "final_score": float(item.final_score) if item.final_score is not None else None,
            "practice_score": float(item.practice_score) if item.practice_score is not None else None,
            "total_score": float(item.total_score) if item.total_score is not None else None,
            "rank": item.ranking,
            "status": item.status.value if hasattr(item.status, 'value') else item.status
        }
        for item in items
    ]

    # 导出Excel
    excel_data = await grade_service.export_excel(
        course_name=record.course_name,
        class_name=record.class_name,
        semester=record.semester,
        items=items_dict,
        weights=record.weights or {"usual": 0.4, "midterm": 0.2, "final": 0.4, "practice": 0.0}
    )

    # 生成文件名
    from urllib.parse import quote
    filename = f"{record.course_name}_{record.class_name or '未知班级'}_{record.semester or '未知学期'}_成绩单.xlsx"
    # 对中文文件名进行URL编码以支持非ASCII字符
    encoded_filename = quote(filename, safe='')

    return StreamingResponse(
        iter([excel_data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
