"""
用户操作日志模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Index
from sqlalchemy.sql import func
from app.models.base import BaseModel


class UserLog(BaseModel):
    """用户操作日志表"""
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    user_type = Column(Enum("student", "teacher"), nullable=False, index=True, comment="用户类型")
    action = Column(String(100), nullable=False, index=True, comment="操作类型")
    module = Column(String(50), nullable=False, index=True, comment="功能模块")
    duration_ms = Column(Integer, default=0, comment="操作耗时（毫秒）")
    success = Column(Integer, default=1, comment="是否成功：1成功 0失败")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="操作时间")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_type": self.user_type,
            "action": self.action,
            "module": self.module,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_msg": self.error_msg,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ApiLog(BaseModel):
    """API调用日志表"""
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    api_name = Column(String(50), nullable=False, index=True, comment="API名称")
    api_type = Column(Enum("xfyun", "other"), default="xfyun", comment="API类型")
    call_type = Column(Enum("success", "fail", "retry"), nullable=False, index=True, comment="调用结果")
    error_code = Column(String(50), nullable=True, comment="错误码")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    response_time_ms = Column(Integer, nullable=True, comment="响应时间（毫秒）")
    request_params = Column(Text, nullable=True, comment="请求参数（脱敏）")
    user_id = Column(Integer, nullable=True, index=True, comment="关联用户ID")
    user_type = Column(Enum("student", "teacher", "admin", "anonymous"), nullable=True, comment="用户类型")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="调用时间")

    def to_dict(self):
        return {
            "id": self.id,
            "api_name": self.api_name,
            "api_type": self.api_type,
            "call_type": self.call_type,
            "error_code": self.error_code,
            "error_msg": self.error_msg,
            "response_time_ms": self.response_time_ms,
            "user_id": self.user_id,
            "user_type": self.user_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class LoginLog(BaseModel):
    """登录日志表"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    user_type = Column(Enum("student", "teacher"), nullable=False, index=True, comment="用户类型")
    login_method = Column(Enum("phone", "wechat", "admin"), nullable=False, comment="登录方式")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="浏览器信息")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="登录时间")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_type": self.user_type,
            "login_method": self.login_method,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }