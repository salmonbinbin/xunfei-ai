"""
API调用日志服务

用于记录讯飞API的调用情况
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models.user_log import ApiLog

logger = logging.getLogger("api_log")


async def save_api_log(
    api_name: str,
    call_type: str,
    response_time_ms: Optional[int] = None,
    error_code: Optional[str] = None,
    error_msg: Optional[str] = None,
    request_params: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    user_type: Optional[str] = None
) -> Optional[int]:
    """
    保存API调用日志

    Args:
        api_name: API名称 (asr, tts, spark, ocr, nlp, ppt)
        call_type: 调用结果 (success, fail, retry)
        response_time_ms: 响应时间（毫秒）
        error_code: 错误码
        error_msg: 错误信息
        request_params: 请求参数（脱敏）
        user_id: 用户ID
        user_type: 用户类型 (student, teacher, admin, anonymous)

    Returns:
        日志记录ID，失败返回None
    """
    try:
        async with AsyncSessionLocal() as db:
            # 脱敏处理：只保存必要的请求参数，不保存敏感信息
            safe_params = None
            if request_params:
                safe_params = json.dumps(request_params, ensure_ascii=False)[:500] if len(json.dumps(request_params)) > 500 else json.dumps(request_params)

            log = ApiLog(
                api_name=api_name,
                api_type="xfyun",
                call_type=call_type,
                error_code=error_code,
                error_msg=error_msg,
                response_time_ms=response_time_ms,
                request_params=safe_params,
                user_id=user_id,
                user_type=user_type
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            logger.info(f"[ApiLog] Saved: api_name={api_name}, call_type={call_type}, response_time={response_time_ms}ms")
            return log.id
    except Exception as e:
        logger.error(f"[ApiLog] Failed to save log: {e}", exc_info=True)
        return None


def get_api_name(api_name: str) -> str:
    """获取API中文名称"""
    api_map = {
        "asr": "语音识别",
        "tts": "语音合成",
        "spark": "星火大模型",
        "ocr": "文字识别",
        "nlp": "NLP分析",
        "ppt": "智能PPT"
    }
    return api_map.get(api_name, api_name)
