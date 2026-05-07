"""
教师认证相关Pydantic模型

定义教师注册、登录、等信息请求响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class TeacherRegisterRequest(BaseModel):
    """教师注册请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码（至少6位）")
    name: str = Field(..., description="姓名")
    department: str = Field(..., description="院系")
    title: Optional[str] = Field(None, description="职称（教授/副教授/讲师）")


class TeacherLoginRequest(BaseModel):
    """教师登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class TeacherResponse(BaseModel):
    """教师响应模型"""
    id: int
    phone: str
    name: str
    department: Optional[str] = None
    title: Optional[str] = None

    class Config:
        from_attributes = True


class TeacherLoginResponse(BaseModel):
    """教师登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    role: str = "teacher"
    teacher: TeacherResponse
