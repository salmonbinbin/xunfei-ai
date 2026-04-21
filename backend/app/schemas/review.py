"""
录音回顾API的Pydantic模型

用于请求/响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewRecordCreate(BaseModel):
    """录音记录创建"""
    record_type: str = Field(..., description="课程/会议")
    title: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    language: Optional[str] = "mandarin"


class ReviewRecordUpdate(BaseModel):
    """录音记录更新"""
    title: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None


class ReviewRecordResponse(BaseModel):
    """录音记录响应"""
    id: int
    user_id: int
    record_type: str
    title: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    language: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    """转写结果响应"""
    id: Optional[int] = None
    record_id: Optional[int] = None
    raw_text: Optional[str] = None
    segments: Optional[list] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    """总结结果响应"""
    id: Optional[int] = None
    record_id: Optional[int] = None
    topic: Optional[str] = None
    key_points: Optional[str] = None
    difficulties: Optional[str] = None
    memorable_quote: Optional[str] = None
    next_suggestion: Optional[str] = None
    discussion_points: Optional[str] = None
    resolutions: Optional[str] = None
    action_items: Optional[str] = None
    full_text: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewDetailResponse(BaseModel):
    """录音回顾详情响应"""
    id: int
    record_type: str
    title: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    language: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    transcription: Optional[TranscriptionResponse] = None
    summary: Optional[SummaryResponse] = None

    class Config:
        from_attributes = True


class ReviewUploadResponse(BaseModel):
    """录音上传响应"""
    success: bool = True
    record_id: int
    message: str
    status: str


class ExportRequest(BaseModel):
    """导出请求"""
    summary_id: int = Field(..., description="总结ID")


class ExportResponse(BaseModel):
    """导出响应"""
    success: bool = True
    message: str
    download_url: Optional[str] = None