from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict


class Settings(BaseSettings):
    """应用配置"""

    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://user:pass@localhost:3306/ai_xiaoshang"

    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # 讯飞开放平台
    XFYUN_APP_ID: str = ""
    XFYUN_API_KEY: str = ""
    XFYUN_API_SECRET: str = ""
    XFYUN_API_PASSWORD: str = ""

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_AUDIO_SIZE_MB: int = 50
    MAX_IMAGE_SIZE_MB: int = 5

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ChromaDB
    CHROMA_DB_PATH: str = "data/chroma_db"

    # 飞书群组配置
    FEISHU_GROUPS: Dict[str, str] = {
        "student_union": "学生会通知",
        "club_alliance": "社团联盟",
        "class_group": "班级通知",
        "youth_union": "团委通知",
        "dormitory": "宿舍管理"
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # 允许额外的环境变量（如FEISHU_WEBHOOK_*）
    )


settings = Settings()
