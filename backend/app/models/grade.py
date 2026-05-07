"""
成绩管理模型

存储成绩记录和成绩明细
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ExamStatus(str, enum.Enum):
    """考试状态枚举"""
    normal = "normal"
    absent = "absent"     # 缺考
    deferred = "deferred"  # 缓考


class GradeRecord(BaseModel):
    """成绩记录表

    存储一次成绩上传的元信息：课程名、班级、权重、AI分析报告等
    """

    __tablename__ = "grade_records"
    __table_args__ = (
        Index("idx_record_teacher", "teacher_id"),
    )

    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_name = Column(String(200), nullable=False)  # 课程名称
    semester = Column(String(50), nullable=True)  # 学期（如2026春季）
    class_name = Column(String(100), nullable=True)  # 班级名称
    file_path = Column(String(500), nullable=True)  # 原始Excel路径
    weights = Column(JSON, nullable=True)  # 成绩权重配置
    ai_report = Column(Text, nullable=True)  # AI分析报告内容
    stats_data = Column(JSON, nullable=True)  # 统计数据（分布、均分等）

    # 关系
    items = relationship("GradeItem", back_populates="record", cascade="all, delete-orphan")


class GradeItem(BaseModel):
    """成绩明细表

    存储每个学生的各项成绩
    """

    __tablename__ = "grade_items"
    __table_args__ = (
        Index("idx_item_record", "record_id"),
        Index("idx_item_rank", "record_id", "ranking"),
    )

    record_id = Column(Integer, ForeignKey("grade_records.id"), nullable=False, index=True)
    student_name = Column(String(100), nullable=False)  # 学生姓名
    student_no = Column(String(50), nullable=True)  # 学号
    usual_score = Column(Numeric(5, 2), nullable=True)  # 平时分
    midterm_score = Column(Numeric(5, 2), nullable=True)  # 期中分
    final_score = Column(Numeric(5, 2), nullable=True)  # 期末分
    practice_score = Column(Numeric(5, 2), nullable=True)  # 实验/实践分
    total_score = Column(Numeric(5, 2), nullable=True)  # 总评
    ranking = Column(Integer, nullable=True)  # 排名
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.normal)  # 考试状态

    # 关系
    record = relationship("GradeRecord", back_populates="items")
