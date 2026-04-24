from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CourseCatalog(BaseModel):
    """课程目录表 - 存储学校开设的所有课程"""

    __tablename__ = "course_catalog"

    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=True, index=True)
    credit = Column(Numeric(3, 1), default=3.0)
    category = Column(String(20), nullable=False)  # 必修/选修/跨专业
    teacher = Column(String(50), nullable=True)
    day_of_week = Column(Integer, nullable=False)  # 周几 1-7
    start_slot = Column(Integer, nullable=False)  # 开始节次 1-12
    end_slot = Column(Integer, nullable=False)  # 结束节次 1-12
    location = Column(String(100), nullable=True)
    capacity = Column(Integer, default=100)
    enrolled = Column(Integer, default=0)
    rating = Column(Numeric(2, 1), default=4.5)
    semester = Column(String(20), nullable=False)  # 学期 2024-1

    # 课程属性
    target_goals = Column(JSON, nullable=True)  # 适用目标 ["考研","就业","考公","出国"]
    prerequisites = Column(JSON, nullable=True)  # 先修课程ID列表
    alternatives = Column(JSON, nullable=True)  # 替代课程ID列表
    tags = Column(JSON, nullable=True)  # 标签 ["核心课","考研必备"]
    description = Column(Text, nullable=True)

    # 课程难度
    difficulty = Column(String(10), default="medium")  # easy/medium/hard

    # 是否启用
    is_active = Column(Integer, default=1)

    def __repr__(self):
        return f"<CourseCatalog {self.name} ({self.code})>"
