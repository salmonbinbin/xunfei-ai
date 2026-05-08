"""
教案 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LessonPlanStatus(str, Enum):
    DRAFT = "draft"
    OUTLINE_READY = "outline_ready"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ChapterContent(BaseModel):
    """章节内容 - 适配讯飞API返回的驼峰命名"""
    chapter_title: str = Field(..., alias="chapterTitle")
    chapter_contents: List[str] = Field(default_factory=list, alias="chapterContents")

    class Config:
        populate_by_name = True


class OutlineData(BaseModel):
    """大纲数据结构 - 适配讯飞API返回的驼峰命名"""
    title: str
    sub_title: Optional[str] = None
    chapters: List[ChapterContent] = []

    class Config:
        populate_by_name = True


class LessonPlanCreateRequest(BaseModel):
    """创建教案请求"""
    title: str = Field(..., min_length=1, max_length=255, description="教案标题")
    course_name: Optional[str] = Field(None, max_length=255, description="课程名称")
    knowledge_points: str = Field(..., min_length=10, description="知识点描述（至少10字）")
    target_audience: Optional[str] = Field(None, max_length=100, description="授课对象")
    teaching_hours: Optional[int] = Field(None, ge=1, le=100, description="课时数")
    template_id: Optional[str] = Field(None, description="PPT模板ID（可选）")


class LessonPlanGenerateOutlineRequest(BaseModel):
    """生成大纲请求"""
    plan_id: int = Field(..., description="教案ID")
    knowledge_points: Optional[str] = Field(None, description="更新的知识点（可选）")


class LessonPlanGeneratePptRequest(BaseModel):
    """生成PPT请求"""
    plan_id: int = Field(..., description="教案ID")
    outline: Dict[str, Any] = Field(..., description="大纲数据（generate-outline返回的outline）")
    template_id: Optional[str] = Field(None, description="PPT模板ID（可选）")
    is_ai_image: bool = Field(False, description="是否AI配图")
    ai_image_type: str = Field("normal", description="AI配图类型: normal/advanced")
    is_card_note: bool = Field(False, description="是否生成演讲备注")


class LessonPlanQueryRequest(BaseModel):
    """查询教案列表"""
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)


class PPTThemeRecord(BaseModel):
    """PPT主题记录"""
    template_index_id: str = Field(..., alias="templateIndexId")
    page_count: int = Field(..., alias="pageCount")
    type: str
    color: str
    industry: str
    style: str
    detail_image: str = Field(..., alias="detailImage")
    pay_type: str = Field(..., alias="payType")

    class Config:
        from_attributes = True
        populate_by_name = True


class PPTThemeListResponse(BaseModel):
    """PPT主题列表响应"""
    total: int
    records: List[PPTThemeRecord]


class LessonPlanResponse(BaseModel):
    """教案响应"""
    id: int
    title: str
    course_name: Optional[str]
    outline: Optional[OutlineData]
    ppt_sid: Optional[str]
    ppt_url: Optional[str]
    template_id: Optional[str]
    status: LessonPlanStatus
    error_msg: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LessonPlanListResponse(BaseModel):
    """教案列表响应"""
    items: List[LessonPlanResponse]
    total: int
    page: int
    page_size: int


class GenerateOutlineResponse(BaseModel):
    """生成大纲响应"""
    success: bool = True
    sid: str
    outline: OutlineData
    message: str = "大纲生成成功"


class GeneratePptResponse(BaseModel):
    """生成PPT响应"""
    success: bool = True
    sid: str
    status: str = "generating"
    message: str = "PPT生成任务已提交"


class PptStatusResponse(BaseModel):
    """PPT状态响应"""
    success: bool = True
    ppt_status: str
    ppt_url: Optional[str] = None
    total_pages: Optional[int] = None
    done_pages: Optional[int] = None
    ai_image_status: Optional[str] = None
    card_note_status: Optional[str] = None