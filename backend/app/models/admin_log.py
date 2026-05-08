"""
管理员操作日志模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.models.base import BaseModel


class AdminLog(BaseModel):
    """管理员操作日志表"""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, index=True, comment="管理员ID")
    admin_name = Column(String(100), nullable=False, comment="管理员昵称（冗余）")
    action = Column(String(100), nullable=False, index=True, comment="操作类型")
    action_text = Column(String(200), nullable=True, comment="操作描述")
    target_type = Column(String(50), nullable=True, comment="操作对象类型")
    target_id = Column(Integer, nullable=True, comment="操作对象ID")
    detail = Column(Text, nullable=True, comment="详细信息（JSON）")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="浏览器信息")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="操作时间")

    def to_dict(self):
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "admin_name": self.admin_name,
            "action": self.action,
            "action_text": self.action_text,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "detail": self.detail,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }