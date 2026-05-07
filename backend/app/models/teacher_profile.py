"""
教师画像模型

存储教师的扩展信息：院系、办公室、职称等
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class TeacherProfile(BaseModel):
    """教师画像表"""

    __tablename__ = "teacher_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(String(100), nullable=True)  # 院系
    office = Column(String(100), nullable=True)  # 办公室
    title = Column(String(50), nullable=True)  # 职称（教授/副教授/讲师）

    # 关系
    user = relationship("User", back_populates="teacher_profile")
