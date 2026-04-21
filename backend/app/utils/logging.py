import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config import settings

# 日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)8s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """创建配置好的Logger实例"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出（按大小轮转）
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# 各模块 Logger
app_logger = setup_logger("app")
xfyun_logger = setup_logger("xfyun")
api_logger = setup_logger("api")
db_logger = setup_logger("database")
