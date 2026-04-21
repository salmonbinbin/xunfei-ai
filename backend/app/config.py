from pydantic_settings import BaseSettings
from typing import Optional


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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
