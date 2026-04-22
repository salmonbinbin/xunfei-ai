"""
AI小商 - FastAPI应用入口

智慧校园AI助手后端服务
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
import time
import uuid
import os

from app.routers import auth, chat, timetable, schedule, review, export, admin, translate
from app.utils.logging import setup_logger, api_logger
from app.config import settings

# 日志配置
logger = setup_logger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()

        # 记录请求
        api_logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)

            # 记录响应
            duration = time.time() - start_time
            api_logger.info(
                f"[{request_id}] Response {response.status_code} "
                f"in {duration:.3f}s"
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            api_logger.error(
                f"[{request_id}] Request failed after {duration:.3f}s: {str(e)}",
                exc_info=True
            )
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info("AI小商 API 启动中...")
    logger.info(f"版本: 1.0.0")
    logger.info(f"配置: {settings.DATABASE_URL[:30]}...")
    logger.info("=" * 50)

    yield

    # 关闭时
    logger.info("AI小商 API 关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="AI小商",
    version="1.0.0",
    description="面向广州商学院师生的智慧校园AI助手",
    lifespan=lifespan
)

# 添加请求日志中间件
app.add_middleware(LoggingMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
# 挂载静态文件目录（用于提供音频等文件访问）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(timetable.router)
app.include_router(schedule.router)
app.include_router(review.router)
app.include_router(export.router)
app.include_router(admin.router)
app.include_router(translate.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI小商 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
