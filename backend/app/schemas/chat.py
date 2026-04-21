from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """消息创建"""
    content: str
    content_type: Optional[str] = "text"
    audio_url: Optional[str] = None


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    conv_id: int
    role: str
    content_type: str
    content: Optional[str] = None
    audio_url: Optional[str] = None
    sentiment: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """会话创建"""
    title: Optional[str] = None
    category: Optional[str] = "general"
    mode: Optional[str] = "normal"


class ConversationUpdate(BaseModel):
    """会话更新"""
    title: Optional[str] = None
    mode: Optional[str] = None
    context_summary: Optional[str] = None


class ConversationResponse(BaseModel):
    """会话响应"""
    id: int
    user_id: int
    title: Optional[str] = None
    category: str
    mode: str
    context_summary: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    conv_id: Optional[int] = Field(None, description="会话ID，不传则创建新会话")
    category: Optional[str] = "general"
    mode: Optional[str] = "normal"


class ChatResponse(BaseModel):
    """聊天响应"""
    conv_id: int
    message_id: int
    content: str
    sentiment: Optional[str] = None
    audio_url: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    conversations: List[ConversationResponse]
    messages: Optional[List[MessageResponse]] = None
