# Teacher routers module
from app.routers.teacher.auth import router as teacher_auth_router
from app.routers.teacher.grade import router as teacher_grade_router

__all__ = ["teacher_auth_router", "teacher_grade_router"]
