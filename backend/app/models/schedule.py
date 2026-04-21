from sqlalchemy import Column, Integer, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Schedule(BaseModel):
    """日程表"""

    __tablename__ = "schedules"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event = Column(String(200), nullable=False)
    event_type = Column(String(20), default="日程")
    day_of_week = Column(Integer, nullable=True)
    time_desc = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)
    is_completed = Column(Integer, default=0)

    # 关系
    user = relationship("User", back_populates="schedules")
