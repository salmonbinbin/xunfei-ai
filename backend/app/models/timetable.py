"""
课表扩展模型

包含课程AI洞察和课程提醒模型
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CourseAIInsight(BaseModel):
    """课程AI洞察表"""
    __tablename__ = "course_ai_insights"

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, unique=True)
    course_summary = Column(Text)
    learning_tips = Column(JSON)
    preview_suggestion = Column(Text)
    review_suggestion = Column(Text)
    key_points = Column(JSON)
    related_courses = Column(JSON)
    difficulty_level = Column(String(10))
    importance = Column(String(10))

    course = relationship("Course", back_populates="ai_insight")


class CourseReminder(BaseModel):
    """课程提醒表"""
    __tablename__ = "course_reminders"

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remind_type = Column(String(20), default="class")
    remind_time = Column(DateTime, nullable=False)
    minutes_before = Column(Integer, default=15)
    message = Column(String(500))
    is_sent = Column(Integer, default=0)
    is_completed = Column(Integer, default=0)

    course = relationship("Course")
    user = relationship("User")
