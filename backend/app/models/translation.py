from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class TranslationTask(BaseModel):
    """翻译任务表"""

    __tablename__ = "translation_tasks"

    task_id = Column(String(64), unique=True, nullable=False)  # 如 trans_xxx
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(20), nullable=False)  # text/document
    source_lang = Column(String(10), nullable=False)  # 如 cn, en, ja
    target_lang = Column(String(10), nullable=False)  # 如 cn, en, ja
    original_content = Column(Text, nullable=True)  # 即时翻译的原文
    original_file_url = Column(String(500), nullable=True)  # 文档翻译的原文件URL
    translated_content = Column(Text, nullable=True)  # 翻译结果
    word_count = Column(Integer, default=0)  # 词数统计
    status = Column(String(20), default="pending")  # pending/processing/completed/failed
    error_message = Column(Text, nullable=True)  # 错误信息

    # 关系
    user = relationship("User")