from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """时间戳混入类"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class BaseModel(Base, TimestampMixin):
    """所有模型的基类"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    async def get_by_id(cls, db, id: int):
        """按ID查询（排除已删除）"""
        from sqlalchemy import and_
        return await db.query(cls).filter(
            and_(cls.id == id, cls.is_deleted == False)
        ).first()

    @classmethod
    async def get_all(cls, db, skip: int = 0, limit: int = 100):
        """获取所有（排除已删除）"""
        from sqlalchemy import and_
        return await db.query(cls).filter(
            cls.is_deleted == False
        ).offset(skip).limit(limit).all()
