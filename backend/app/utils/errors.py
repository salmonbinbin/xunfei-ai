from fastapi import HTTPException, status
from typing import Optional, Any
import traceback
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用级异常基类"""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self):
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class NotFoundException(AppException):
    """资源不存在"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            status_code=404
        )


class ValidationException(AppException):
    """数据验证失败"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class UnauthorizedException(AppException):
    """未授权"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )


class ThirdPartyException(AppException):
    """第三方服务异常（如讯飞API）"""

    def __init__(self, service: str, message: str, original_error: Exception = None):
        logger.error(f"[{service}] Third party error: {message}", exc_info=original_error)
        super().__init__(
            message=f"{service} error: {message}",
            code="THIRD_PARTY_ERROR",
            status_code=502,
            details={"service": service, "original_error": str(original_error)}
        )


# 异常处理装饰器
from functools import wraps


def handle_app_errors(func):
    """统一异常处理装饰器"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # HTTPException 直接抛出，不拦截
            raise
        except AppException as e:
            # AppException 转为 HTTPException 返回 JSON 响应
            raise HTTPException(
                status_code=e.status_code,
                detail=e.to_dict()
            )
        except Exception as e:
            logger.error(f"[{func.__name__}] Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Internal server error",
                        "details": str(e) if __debug__ else None
                    }
                }
            )

    return wrapper
