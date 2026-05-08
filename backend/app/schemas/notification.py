"""
教师通知 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationGenerateRequest(BaseModel):
    """生成通知请求"""
    notification_type: str = Field(..., description="通知类型: exam/meeting/activity/holiday/submission/other")
    topic: str = Field(..., description="通知主题", min_length=1)
    additional_info: Optional[str] = Field(None, description="补充信息")


class NotificationGenerateResponse(BaseModel):
    """生成通知响应"""
    success: bool = True
    title: str
    content: str
    message: str = "通知生成成功"


class NotificationSendRequest(BaseModel):
    """发送通知请求"""
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    group_id: str = Field(..., description="飞书群组ID")


class NotificationGroup(BaseModel):
    """通知群组"""
    group_id: str
    name: str


class NotificationRecord(BaseModel):
    """通知记录"""
    id: int
    notification_type: str
    title: str
    content: str
    additional_info: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
