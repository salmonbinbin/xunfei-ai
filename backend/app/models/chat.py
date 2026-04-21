from sqlalchemy import Column, Integer, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Conversation(BaseModel):
    """对话会话"""

    __tablename__ = "conversations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    category = Column(String(20), default="general")
    mode = Column(String(20), default="normal")  # normal/emotion
    context_summary = Column(Text, nullable=True)
    message_count = Column(Integer, default=0)

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(BaseModel):
    """消息记录"""

    __tablename__ = "messages"

    conv_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(10), nullable=False)  # user/assistant
    content_type = Column(String(20), default="text")  # text/voice
    content = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    sentiment = Column(String(20), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")
