import logging

from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

logger = logging.getLogger("database")


class ReviewRecord(BaseModel):
    """录音回顾记录

    用于存储用户的录音回顾信息，包括课程录音和会议录音。
    支持软删除，包含时间戳，自动跟踪创建和更新时间。
    """

    __tablename__ = "review_records"
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    record_type = Column(String(10), nullable=False)  # 课程/会议
    title = Column(String(200), nullable=True)
    audio_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # 时长(秒)
    language = Column(String(20), default="mandarin")
    status = Column(String(20), default="pending")  # pending/processing/completed/failed

    # 关系
    user = relationship("User", back_populates="review_records")
    transcription = relationship("Transcription", back_populates="record", uselist=False)
    summary = relationship("Summary", back_populates="record", uselist=False)


class Transcription(BaseModel):
    """转写结果

    存储录音的转写结果，包含原始文本和分段信息。
    与ReviewRecord一对一关联。
    """

    __tablename__ = "transcriptions"

    record_id = Column(Integer, ForeignKey("review_records.id"), unique=True, nullable=False)
    raw_text = Column(Text, nullable=True)  # 原始转写文字
    segments = Column(JSON, nullable=True)  # 分段结果

    # 关系
    record = relationship("ReviewRecord", back_populates="transcription")


class Summary(BaseModel):
    """总结结果

    存储录音的AI总结结果。
    课程类型包含：topic, key_points, difficulties, memorable_quote, next_suggestion, full_text
    会议类型包含：topic, discussion_points, resolutions, action_items, full_text
    与ReviewRecord一对一关联。
    """

    __tablename__ = "summaries"

    record_id = Column(Integer, ForeignKey("review_records.id"), unique=True, nullable=False)
    topic = Column(String(200), nullable=True)  # 主题
    key_points = Column(Text, nullable=True)  # 核心知识点（课程用）
    difficulties = Column(Text, nullable=True)  # 重点难点（课程用）
    memorable_quote = Column(String(500), nullable=True)  # 金句
    next_suggestion = Column(Text, nullable=True)  # 预习建议（课程用）
    discussion_points = Column(Text, nullable=True)  # 讨论要点（会议用）
    resolutions = Column(Text, nullable=True)  # 决议（会议用）
    action_items = Column(Text, nullable=True)  # 行动项（会议用）
    full_text = Column(Text, nullable=True)  # 完整总结

    # 关系
    record = relationship("ReviewRecord", back_populates="summary")
