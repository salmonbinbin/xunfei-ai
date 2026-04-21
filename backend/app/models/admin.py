from sqlalchemy import Column, Integer, String, DateTime, Integer
from app.models.base import BaseModel


class AdminUser(BaseModel):
    """管理员表"""

    __tablename__ = "admin_users"

    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), default="admin")
    nickname = Column(String(50), nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)
