# Teacher routers module
from app.routers.teacher.auth import router as teacher_auth_router
from app.routers.teacher.grade import router as teacher_grade_router
from app.routers.teacher.notification import router as teacher_notification_router
from app.routers.teacher.lesson_plan import router as teacher_lesson_plan_router

__all__ = [
    "teacher_auth_router",
    "teacher_grade_router",
    "teacher_notification_router",
    "teacher_lesson_plan_router",
]
