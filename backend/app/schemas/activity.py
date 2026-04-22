"""
校园活动助手API的Pydantic模型

用于请求/响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class GeneratePlanRequest(BaseModel):
    """生成活动策划方案请求"""
    activity_type: str = Field(
        ...,
        description="活动类型：文艺类、体育类、学术类、志愿类、团建类、其他"
    )
    theme: str = Field(..., description="活动主题，如：校园歌手大赛")
    scale: str = Field(
        ...,
        description="预计人数：小规模(≤50)、中规模(50-200)、大规模(≥200)"
    )
    budget: str = Field(
        ...,
        description="预算范围：低(<500元)、中(500-2000元)、高(>2000元)"
    )
    activity_time: Optional[str] = Field(None, description="活动时间：初步意向日期")
    special_needs: Optional[List[str]] = Field(
        default=None,
        description="特殊需求：需要抽奖、需要嘉宾、室外活动、线上活动"
    )


class GeneratePlanResponse(BaseModel):
    """生成活动策划方案响应"""
    success: bool = True
    plan: str = Field(..., description="生成的策划方案内容")
    message: str = "策划方案生成成功"


class GenerateCopyRequest(BaseModel):
    """生成宣传文案请求"""
    activity_name: str = Field(..., description="活动名称")
    activity_content: Optional[str] = Field(None, description="活动概述内容")
    copy_type: str = Field(
        ...,
        description="文案类型：海报主标题、朋友圈短文案、公众号推文、邀请函、广播稿"
    )
    style: str = Field(
        default="活泼青春",
        description="文案风格：正式严肃、活泼青春、温情暖心、燃系热血"
    )


class GenerateCopyResponse(BaseModel):
    """生成宣传文案响应"""
    success: bool = True
    copy: str = Field(..., description="生成的文案内容")
    copy_type: str = Field(..., description="文案类型")
    style: str = Field(..., description="文案风格")
    message: str = "文案生成成功"


class SendFeishuRequest(BaseModel):
    """发送到飞书群请求"""
    group_id: str = Field(
        ...,
        description="群组标识：student_union、club_alliance、class_group、youth_union、dormitory"
    )
    title: str = Field(..., description="消息标题")
    content: str = Field(..., description="消息内容（支持换行）")


class SendFeishuResponse(BaseModel):
    """发送到飞书群响应"""
    success: bool = True
    message: str = "消息发送成功"
    group_id: str = Field(..., description="发送到的群组ID")
    group_name: Optional[str] = Field(None, description="群组名称")


class AvailableGroupsResponse(BaseModel):
    """可用群组列表响应"""
    success: bool = True
    groups: List[dict] = Field(
        ...,
        description="可用群组列表，每项包含 id 和 name"
    )
