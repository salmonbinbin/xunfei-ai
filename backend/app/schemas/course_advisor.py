"""
智能选课助手API的Pydantic模型

用于请求/响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProfileResponse(BaseModel):
    """学生画像响应"""
    success: bool = True
    major: str = Field(..., description="专业")
    grade: int = Field(..., description="年级")
    goal: str = Field(..., description="目标：考研/考公/就业/出国/未定")
    gpa: Optional[float] = Field(None, description="GPA")
    completed_credits: int = Field(..., description="已修学分")
    required_credits: int = Field(..., description="要求总学分")
    radar_data: Dict[str, int] = Field(..., description="雷达图数据：专业知识覆盖度、能力偏向、目标匹配度、选课压力")
    ability_type: str = Field(..., description="能力偏向：逻辑型/记忆型/创意型")
    ai_suggestion: str = Field(..., description="AI建议")


class CourseBase(BaseModel):
    """课程基础信息"""
    id: int
    name: str
    teacher: str
    credits: int
    day_of_week: int = Field(..., description="星期几 1-7")
    start_slot: int = Field(..., description="开始节次 1-12")
    end_slot: int = Field(..., description="结束节次 1-12")
    location: Optional[str] = None
    rating: float = Field(..., description="评分")
    enrolled: int = Field(..., description="已选人数")
    capacity: int = Field(..., description="容量")
    tags: List[str] = Field(default_factory=list, description="标签")
    description: Optional[str] = None


class CourseWithConflict(CourseBase):
    """课程信息（含冲突检测）"""
    conflict_status: str = Field(default="none", description="冲突状态：none/warning/error")
    conflict_info: Optional[str] = Field(None, description="冲突信息")


class RecommendRequest(BaseModel):
    """推荐请求"""
    semester: str = Field(..., description="学期，如 2024-1")
    category: str = Field(default="all", description="类别：all/mandatory/elective/cross_major")
    goal_filter: Optional[str] = Field(None, description="目标筛选：考研/考公/就业/出国")
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=3, description="每页数量")


class CourseDetailResponse(BaseModel):
    """课程详情响应"""
    success: bool = True
    course: Dict[str, Any] = Field(..., description="课程详情")
    prerequisites: List[Dict[str, Any]] = Field(default_factory=list, description="先修课程")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="替代课程")
    popular_combinations: List[str] = Field(default_factory=list, description="热门搭配")


class RecommendResponse(BaseModel):
    """推荐响应"""
    success: bool = True
    courses: List[Dict[str, Any]] = Field(..., description="推荐课程列表")
    total_credits: int = Field(..., description="总学分")
    message: str = "推荐成功"
    total: int = Field(default=0, description="总课程数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=5, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")


class ChatRequest(BaseModel):
    """对话咨询请求"""
    message: str = Field(..., description="用户消息")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="对话历史")


class ChatResponse(BaseModel):
    """对话咨询响应"""
    success: bool = True
    reply: str = Field(..., description="AI回复")
    recommended_courses: Optional[List[Dict[str, Any]]] = Field(None, description="推荐的课程列表")
    suggestions: Optional[List[str]] = Field(None, description="建议列表")


class ConfirmRequest(BaseModel):
    """确认选课方案请求"""
    semester: str = Field(..., description="学期")
    selected_courses: List[int] = Field(..., description="选中的课程ID列表")


class ConfirmResponse(BaseModel):
    """确认选课方案响应"""
    success: bool = True
    plan_id: int = Field(..., description="方案ID")
    message: str = "选课方案已保存"
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="冲突列表")
    total_credits: int = Field(..., description="总学分")


class ScheduleConflict(BaseModel):
    """课程时间冲突"""
    course_id: int
    course_name: str
    conflicting_course_id: int
    conflicting_course_name: str
    day_of_week: int
    slots: List[int]
    conflict_type: str = Field(default="time", description="冲突类型：time/same_teacher/similar")