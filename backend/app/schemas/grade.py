"""
成绩管理相关Pydantic模型

定义成绩上传、查询、统计等请求响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GradeWeights(BaseModel):
    """成绩权重配置"""
    usual: float = Field(default=0.4, description="平时分权重")
    midterm: float = Field(default=0.2, description="期中分权重")
    final: float = Field(default=0.4, description="期末分权重")
    practice: float = Field(default=0.0, description="实验分权重")


class GradeUploadRequest(BaseModel):
    """成绩上传请求（用于解析后的元数据）"""
    course_name: str = Field(..., description="课程名称")
    semester: Optional[str] = Field(None, description="学期")
    class_name: Optional[str] = Field(None, description="班级名称")
    weights: Optional[GradeWeights] = Field(
        default_factory=lambda: GradeWeights(),
        description="成绩权重配置"
    )


class GradeItemBase(BaseModel):
    """成绩明细基础模型"""
    student_name: str = Field(..., description="学生姓名")
    student_no: Optional[str] = Field(None, description="学号")
    usual_score: Optional[float] = Field(None, description="平时分")
    midterm_score: Optional[float] = Field(None, description="期中分")
    final_score: Optional[float] = Field(None, description="期末分")
    practice_score: Optional[float] = Field(None, description="实验/实践分")
    total_score: Optional[float] = Field(None, description="总评")
    rank: Optional[int] = Field(None, description="排名")
    status: str = Field(default="normal", description="考试状态")


class GradeItemResponse(GradeItemBase):
    """成绩明细响应模型"""
    id: int

    class Config:
        from_attributes = True


class GradeDistributionItem(BaseModel):
    """成绩分布条目"""
    range: str = Field(..., description="分数区间")
    count: int = Field(..., description="人数")


class GradeBasicStats(BaseModel):
    """基础统计"""
    total_students: int = Field(..., description="总人数")
    avg_score: float = Field(..., description="平均分")
    pass_rate: float = Field(..., description="及格率")
    max_score: float = Field(..., description="最高分")
    min_score: float = Field(..., description="最低分")


class GradeComponentStats(BaseModel):
    """单项成绩统计"""
    avg: float = Field(..., description="平均分")
    max: float = Field(..., description="最高分")
    min: float = Field(..., description="最低分")


class GradeStatsResponse(BaseModel):
    """成绩统计数据响应"""
    basic: GradeBasicStats
    distribution: List[GradeDistributionItem]
    by_component: Optional[Dict[str, GradeComponentStats]] = Field(
        None, description="各单项成绩统计"
    )


class GradeRecordListItem(BaseModel):
    """成绩记录列表项"""
    id: int
    course_name: str
    class_name: Optional[str] = None
    semester: Optional[str] = None
    student_count: int = Field(..., description="学生人数")
    avg_score: Optional[float] = Field(None, description="平均分")
    pass_rate: Optional[float] = Field(None, description="及格率")
    created_at: datetime

    class Config:
        from_attributes = True


class GradeRecordListResponse(BaseModel):
    """成绩记录列表响应"""
    records: List[GradeRecordListItem]
    total: int
    page: int
    page_size: int


class GradeRecordDetailResponse(BaseModel):
    """成绩记录详情响应"""
    id: int
    course_name: str
    class_name: Optional[str] = None
    semester: Optional[str] = None
    weights: Dict[str, float]
    items: List[GradeItemResponse]
    stats: GradeStatsResponse

    class Config:
        from_attributes = True


class ExamAnalysis(BaseModel):
    """试卷分析"""
    difficulty: float = Field(..., description="难度系数")
    difficulty_text: str = Field(..., description="难度描述")
    discrimination: float = Field(..., description="区分度")
    discrimination_text: str = Field(..., description="区分度描述")


class AIReportResponse(BaseModel):
    """AI分析报告响应"""
    course_name: str
    semester: Optional[str] = None
    summary: str = Field(..., description="班级整体概述")
    high_performers: List[str] = Field(default_factory=list, description="高分学生名单")
    needs_attention: List[str] = Field(default_factory=list, description="需要关注的学生")
    exam_analysis: ExamAnalysis
    suggestions: str = Field(..., description="教学建议")


class GradeUploadResponse(BaseModel):
    """成绩上传响应"""
    record_id: int
    course_name: str
    item_count: int
    stats: GradeBasicStats


class GradeDeleteResponse(BaseModel):
    """成绩删除响应"""
    success: bool
    message: str = "删除成功"
