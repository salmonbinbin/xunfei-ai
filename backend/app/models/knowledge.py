from sqlalchemy import Column, Integer, String, DateTime, Integer, Text
from app.models.base import BaseModel


class KnowledgeBase(BaseModel):
    """知识库"""

    __tablename__ = "knowledge_base"

    category = Column(String(50), nullable=False)
    question = Column(String(500), nullable=True)
    answer = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    content_vector = Column(Text, nullable=True)  # 向量存储
    source = Column(String(200), nullable=True)
    is_active = Column(Integer, default=1)
    views = Column(Integer, default=0)
