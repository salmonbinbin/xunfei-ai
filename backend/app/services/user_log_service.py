"""
用户操作日志服务

用于记录用户在各功能模块的操作行为
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import AsyncSessionLocal
from app.models.user_log import UserLog

logger = logging.getLogger("user_log")


async def save_user_log(
    user_id: int,
    user_type: str,
    action: str,
    module: str,
    duration_ms: int = 0,
    success: bool = True,
    error_msg: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Optional[int]:
    """
    保存用户操作日志

    Args:
        user_id: 用户ID
        user_type: 用户类型 (student/teacher)
        action: 操作类型 (ai_chat, voice_input, upload_audio, etc)
        module: 功能模块 (ai_sister, review, timetable, translate, etc)
        duration_ms: 操作耗时（毫秒）
        success: 是否成功
        error_msg: 错误信息
        ip_address: 用户IP

    Returns:
        日志记录ID，失败返回None
    """
    try:
        async with AsyncSessionLocal() as db:
            log = UserLog(
                user_id=user_id,
                user_type=user_type,
                action=action,
                module=module,
                duration_ms=duration_ms,
                success=1 if success else 0,
                error_msg=error_msg,
                ip_address=ip_address
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            logger.info(f"[UserLog] Saved: user_id={user_id}, action={action}, module={module}, success={success}")
            return log.id
    except Exception as e:
        logger.error(f"[UserLog] Failed to save log: {e}", exc_info=True)
        return None


def get_module_name(module: str) -> str:
    """获取模块中文名称"""
    module_map = {
        "ai_sister": "AI学姐对话",
        "review": "录音回顾",
        "timetable": "课表管理",
        "translate": "智能翻译",
        "course_advisor": "选课助手",
        "activity": "校园活动",
        "grade": "成绩管理",
        "notification": "通知发布",
        "lesson_plan": "备课教案"
    }
    return module_map.get(module, module)


def get_action_name(action: str) -> str:
    """获取操作类型中文名称"""
    action_map = {
        "ai_chat": "AI对话",
        "ai_chat_streaming": "AI流式对话",
        "voice_input": "语音输入",
        "voice_output": "语音输出",
        "upload_audio": "上传录音",
        "upload_timetable": "上传课表",
        "import_timetable": "导入课表",
        "translate_text": "文本翻译",
        "translate_doc": "文档翻译",
        "course_recommend": "选课推荐",
        "activity_plan": "活动策划",
        "activity_copy": "宣传文案",
        "grade_upload": "成绩上传",
        "grade_view": "成绩查看",
        "notification_generate": "通知生成",
        "notification_send": "通知发送",
        "lesson_plan_generate": "教案生成",
        "lesson_plan_ppt": "PPT生成"
    }
    return action_map.get(action, action)
