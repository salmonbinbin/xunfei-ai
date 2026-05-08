"""
管理员模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Admin(BaseModel):
    """管理员表"""
    __tablename__ = "admins"

    username = Column(String(50), unique=True, nullable=False, index=True, comment="管理员用户名")
    password = Column(String(255), nullable=False, comment="密码（哈希）")
    nickname = Column(String(100), nullable=False, comment="昵称")
    role = Column(String(20), default="super_admin", comment="角色：super_admin/auditor")
    status = Column(Enum("active", "disabled"), default="active", index=True, comment="状态")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    login_count = Column(Integer, default=0, comment="登录次数")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
            "status": self.status,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 保留旧的 AdminUser 名称引用以保持兼容性
AdminUser = Admin