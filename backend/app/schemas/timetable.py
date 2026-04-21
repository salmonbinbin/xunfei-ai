from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CourseCreate(BaseModel):
    """课程创建"""
    name: str = Field(..., description="课程名")
    code: Optional[str] = None
    credit: Optional[float] = None
    category: Optional[str] = None
    day_of_week: int = Field(..., ge=1, le=7, description="周几")
    start_slot: int = Field(..., ge=1, le=12, description="开始节次")
    end_slot: int = Field(..., ge=1, le=12, description="结束节次")
    week_range: Optional[str] = "1-16周"
    location: Optional[str] = None
    teacher: Optional[str] = None
    ai_tip: Optional[str] = None


class CourseUpdate(BaseModel):
    """课程更新"""
    name: Optional[str] = None
    code: Optional[str] = None
    credit: Optional[float] = None
    category: Optional[str] = None
    day_of_week: Optional[int] = None
    start_slot: Optional[int] = None
    end_slot: Optional[int] = None
    week_range: Optional[str] = None
    location: Optional[str] = None
    teacher: Optional[str] = None
    ai_tip: Optional[str] = None
    is_active: Optional[int] = None


class CourseResponse(BaseModel):
    """课程响应"""
    id: int
    user_id: int
    name: str
    code: Optional[str] = None
    credit: Optional[float] = None
    category: Optional[str] = None
    day_of_week: int
    start_slot: int
    end_slot: int
    week_range: Optional[str] = None
    location: Optional[str] = None
    teacher: Optional[str] = None
    ai_tip: Optional[str] = None
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class TodayCoursesResponse(BaseModel):
    """今日课程响应"""
    date: str
    day_of_week: int
    class_name: Optional[str] = None  # 用户班别
    courses: List[CourseResponse]
    schedules: List["ScheduleResponse"] = []


class ScheduleCreate(BaseModel):
    """日程创建"""
    event: str = Field(..., description="日程内容")
    event_type: Optional[str] = "日程"
    day_of_week: Optional[int] = None
    time_desc: Optional[str] = None
    location: Optional[str] = None


class ScheduleUpdate(BaseModel):
    """日程更新"""
    event: Optional[str] = None
    event_type: Optional[str] = None
    day_of_week: Optional[int] = None
    time_desc: Optional[str] = None
    location: Optional[str] = None
    is_completed: Optional[int] = None


class ScheduleResponse(BaseModel):
    """日程响应"""
    id: int
    user_id: int
    event: str
    event_type: str
    day_of_week: Optional[int] = None
    time_desc: Optional[str] = None
    location: Optional[str] = None
    is_completed: int
    created_at: datetime

    class Config:
        from_attributes = True


class TimetableImportRequest(BaseModel):
    """课表导入请求"""
    courses: List[Dict[str, Any]] = Field(..., description="课程列表")
    semester_start_date: Optional[str] = Field(None, description="学期开始日期，如2025-03-03")


class TimetableImportResponse(BaseModel):
    """课表导入响应"""
    message: str
    courses_count: int
    courses: Optional[List[Dict[str, Any]]] = None
    raw_markdown: Optional[str] = None


class AIInsightResponse(BaseModel):
    """课程AI洞察响应"""
    course_summary: Optional[str] = None
    learning_tips: Optional[List[str]] = None
    preview_suggestion: Optional[str] = None
    review_suggestion: Optional[str] = None
    key_points: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    importance: Optional[str] = None

    class Config:
        from_attributes = True


class CourseWithAIResponse(BaseModel):
    """课程详情响应（包含AI洞察）"""
    id: int
    user_id: int
    name: str
    code: Optional[str] = None
    credit: Optional[float] = None
    category: Optional[str] = None
    day_of_week: int
    start_slot: int
    end_slot: int
    week_range: Optional[str] = None
    location: Optional[str] = None
    teacher: Optional[str] = None
    ai_tip: Optional[str] = None
    is_active: int
    created_at: datetime
    ai_insight: Optional[AIInsightResponse] = None

    class Config:
        from_attributes = True


class AIChatRequest(BaseModel):
    """AI学伴问答请求"""
    course_id: int
    question: str


class AIChatResponse(BaseModel):
    """AI学伴问答响应"""
    answer: str
    course_id: int
