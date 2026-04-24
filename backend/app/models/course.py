from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Course(BaseModel):
    """课程表"""

    __tablename__ = "courses"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    credit = Column(Numeric(3, 1), nullable=True)
    category = Column(String(20), nullable=True)  # 通识/专业/选修
    day_of_week = Column(Integer, nullable=False)  # 周几1-7
    start_slot = Column(Integer, nullable=False)  # 第几节
    end_slot = Column(Integer, nullable=False)  # 第几节
    week_range = Column(String(20), default="1-16周")
    location = Column(String(100), nullable=True)
    teacher = Column(String(50), nullable=True)
    ai_tip = Column(String(200), nullable=True)
    is_active = Column(Integer, default=1)
    course_date = Column(Date, nullable=True)  # 课程日期（根据学期开始日期计算）
    source = Column(String(20), default="手动")  # 课程来源：手动/选课助手

    # 关系
    user = relationship("User", back_populates="courses")
    ai_insight = relationship("CourseAIInsight", back_populates="course", uselist=False)
