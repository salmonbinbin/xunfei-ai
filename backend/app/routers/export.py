"""
导出路由

DOCX/PPTX文档生成导出
"""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import io

from app.database import get_db
from app.models.user import User
from app.models.review import Summary, ReviewRecord
from app.schemas.review import ExportRequest
from app.services.docx_generator import docx_generator
from app.services.pptx_generator import pptx_generator
from app.utils.auth import get_current_user
from app.utils.errors import handle_app_errors, NotFoundException, ValidationException

logger = logging.getLogger("api")

router = APIRouter(prefix="/api/export", tags=["导出"])


# ============ 导出DOCX ============

@router.post("/docx")
@handle_app_errors
async def export_to_docx(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    导出录音回顾总结为DOCX文档

    请求：{summary_id: int}
    响应：文件流（.docx）
    """
    logger.info(f"[Export] Export to DOCX - summary_id: {request.summary_id}, user: {current_user.id}")

    # 查询总结记录
    result = await db.execute(
        select(Summary).where(Summary.id == request.summary_id)
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise NotFoundException("Summary", request.summary_id)

    # 查询关联的录音记录，验证权限
    record_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == summary.record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = record_result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", summary.record_id)

    # 生成DOCX文件
    try:
        docx_bytes = await docx_generator.generate_review_summary(
            title=record.title or "录音回顾总结",
            topic=summary.topic or "",
            key_points=summary.key_points or "",
            difficulties=summary.difficulties or "",
            memorable_quote=summary.memorable_quote or "",
            next_suggestion=summary.next_suggestion or "",
            full_text=summary.full_text or "",
            metadata={
                "record_type": record.record_type,
                "language": record.language,
                "created_at": record.created_at.isoformat() if record.created_at else ""
            }
        )

        # 生成文件名
        filename = f"review_summary_{record.id}_{request.summary_id}.docx"

        logger.info(f"[Export] DOCX generated successfully for summary: {request.summary_id}")

        return StreamingResponse(
            io.BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except NotImplementedError as e:
        logger.error(f"[Export] DOCX generation not implemented: {e}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="DOCX导出功能待实现"
        )
    except Exception as e:
        logger.error(f"[Export] DOCX generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOCX导出失败: {str(e)}"
        )


# ============ 导出PPTX ============

@router.post("/pptx")
@handle_app_errors
async def export_to_pptx(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    导出录音回顾总结为PPTX文档

    请求：{summary_id: int}
    响应：文件流（.pptx）
    """
    logger.info(f"[Export] Export to PPTX - summary_id: {request.summary_id}, user: {current_user.id}")

    # 查询总结记录
    result = await db.execute(
        select(Summary).where(Summary.id == request.summary_id)
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise NotFoundException("Summary", request.summary_id)

    # 查询关联的录音记录，验证权限
    record_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.id == summary.record_id,
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.is_deleted == False
            )
        )
    )
    record = record_result.scalar_one_or_none()

    if not record:
        raise NotFoundException("ReviewRecord", summary.record_id)

    # 生成PPTX文件
    try:
        pptx_bytes = await pptx_generator.generate_review_summary(
            title=record.title or "录音回顾总结",
            topic=summary.topic or "",
            key_points=summary.key_points or "",
            difficulties=summary.difficulties or "",
            memorable_quote=summary.memorable_quote or "",
            next_suggestion=summary.next_suggestion or "",
            full_text=summary.full_text or "",
            metadata={
                "record_type": record.record_type,
                "language": record.language,
                "created_at": record.created_at.isoformat() if record.created_at else ""
            }
        )

        # 生成文件名
        filename = f"review_summary_{record.id}_{request.summary_id}.pptx"

        logger.info(f"[Export] PPTX generated successfully for summary: {request.summary_id}")

        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except NotImplementedError as e:
        logger.error(f"[Export] PPTX generation not implemented: {e}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PPTX导出功能待实现"
        )
    except Exception as e:
        logger.error(f"[Export] PPTX generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPTX导出失败: {str(e)}"
        )