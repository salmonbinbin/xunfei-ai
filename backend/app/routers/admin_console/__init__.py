# Admin console routers
from app.routers.admin_console.auth import router as admin_auth_router
from app.routers.admin_console.dashboard import router as admin_dashboard_router
from app.routers.admin_console.user import router as admin_user_router
from app.routers.admin_console.log import router as admin_log_router

__all__ = [
    "admin_auth_router",
    "admin_dashboard_router",
    "admin_user_router",
    "admin_log_router"
]