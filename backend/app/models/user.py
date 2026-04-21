from sqlalchemy import Column, Integer, String, DateTime, Boolean, Integer, Numeric, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """用户表"""

    __tablename__ = "users"

    openid = Column(String(64), nullable=True)
    unionid = Column(String(64), nullable=True)
    nickname = Column(String(64), nullable=True)
    phone = Column(String(20), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Integer, default=1)
    last_login = Column(DateTime, nullable=True)

    # 关系
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    courses = relationship("Course", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    review_records = relationship("ReviewRecord", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class StudentProfile(BaseModel):
    """学生画像表"""

    __tablename__ = "student_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    major = Column(String(100), nullable=True)
    grade = Column(Integer, nullable=True)  # 年级1-4
    class_name = Column(String(50), nullable=True)
    goal = Column(String(20), nullable=True)  # 考研/考公/就业/出国/未定
    goal_detail = Column(Text, nullable=True)
    voice_prefer = Column(Integer, default=1)  # 偏好语音
    emotion_mode = Column(String(20), default="normal")  # normal/emotion
    gpa = Column(Numeric(3, 2), nullable=True)
    completed_courses = Column(JSON, nullable=True)

    # 关系
    user = relationship("User", back_populates="student_profile")
