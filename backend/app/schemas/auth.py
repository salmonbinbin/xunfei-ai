"""
认证相关Pydantic模型

定义登录、注册、用户信息等请求响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """用户登录请求（账号密码）"""
    username: str = Field(..., description="用户名（手机号）")
    password: str = Field(..., description="密码")


class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., description="用户名（手机号）")
    password: str = Field(..., min_length=6, description="密码（至少6位）")
    nickname: Optional[str] = Field(None, description="昵称")


class ProfileRequest(BaseModel):
    """学生画像更新请求"""
    major: Optional[str] = Field(None, description="专业")
    grade: Optional[int] = Field(None, description="年级（1-4）")
    class_name: Optional[str] = Field(None, description="班级")
    goal: Optional[str] = Field(None, description="目标：考研/考公/就业/出国/未定")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    has_profile: bool = False

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class StudentProfileBase(BaseModel):
    """学生画像基础模型"""
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None
    goal: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    """学生画像创建"""
    pass


class StudentProfileUpdate(StudentProfileBase):
    """学生画像更新"""
    goal_detail: Optional[str] = None
    voice_prefer: Optional[bool] = True
    emotion_mode: Optional[str] = "normal"


class StudentProfileResponse(BaseModel):
    """学生画像响应"""
    id: int
    user_id: int
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None
    goal: Optional[str] = None
    goal_detail: Optional[str] = None
    voice_prefer: bool = True
    emotion_mode: str = "normal"
    gpa: Optional[float] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """用户创建模型"""
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserDetailResponse(BaseModel):
    """用户详细信息响应"""
    id: int
    openid: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    has_profile: bool = False
    profile: Optional[StudentProfileResponse] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminLogin(BaseModel):
    """管理员登录"""
    username: str
    password: str


class AdminResponse(BaseModel):
    """管理员响应"""
    id: int
    username: str
    nickname: Optional[str] = None
    role: str
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
