"""
通知服务 - AI生成通知 + 飞书推送
"""
import logging
from typing import Dict, Any, Optional, List

from app.services.xinghuo_service import xinghuo_service
from app.services.feishu_service import feishu_service

logger = logging.getLogger("notification_service")

# 通知类型映射
NOTIFICATION_TYPE_MAPPING = {
    "exam": "期末/期中考试安排",
    "meeting": "教师/班级会议通知",
    "activity": "校园活动通知",
    "holiday": "放假通知",
    "submission": "征文/投稿征集通知",
    "other": "一般通知"
}


class NotificationService:
    """通知服务类"""

    async def generate_notification(
        self,
        notification_type: str,
        topic: str,
        additional_info: Optional[str] = None
    ) -> Dict[str, str]:
        """
        AI生成通知

        Args:
            notification_type: 通知类型
            topic: 通知主题
            additional_info: 补充信息

        Returns:
            {"title": str, "content": str}

        Raises:
            Exception: 如果生成失败
        """
        logger.info(f"[NotificationService] 生成通知开始: type={notification_type}, topic={topic}")
        logger.info(f"[NotificationService] additional_info={additional_info}")

        # 构建prompt
        type_desc = NOTIFICATION_TYPE_MAPPING.get(notification_type, "一般通知")

        prompt = f"""你是一个广州商学院的行政秘书，负责生成格式规范的通知文档。

要求：
1. 标题格式：【通知】+ 主题
2. 开头称呼：尊敬的各位同学/老师
3. 正文分点列出，逻辑清晰，使用中文数字（一、二、三）
4. 结尾落款：广州商学院XX学院 + 日期
5. 语气正式，内容准确

输入信息：
- 通知类型：{type_desc}
- 通知主题：{topic}
- 补充信息：{additional_info or '无'}

请严格按照上述格式生成通知，直接输出通知内容，不要添加标题或说明文字。"""

        logger.info(f"[NotificationService] prompt构建完成，长度={len(prompt)}")

        # 调用星火大模型
        try:
            logger.info(f"[NotificationService] 开始调用星火大模型...")
            messages = [{"role": "user", "content": prompt}]
            logger.debug(f"[NotificationService] messages={messages}")

            content = await xinghuo_service.chat_with_retry(
                messages=messages,
                user_id="notification",
                temperature=0.7,
                max_tokens=2048
            )

            logger.info(f"[NotificationService] 星火调用成功，content长度={len(content) if content else 0}")

        except Exception as e:
            logger.error(f"[NotificationService] 星火调用失败: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

        if not content:
            logger.error(f"[NotificationService] 星火返回内容为空")
            raise Exception("AI生成内容为空")

        # 构造标题
        title = f"【通知】{topic}"

        logger.info(f"[NotificationService] 通知生成成功: title={title}")

        return {
            "title": title,
            "content": content
        }

    def get_available_groups(self) -> List[Dict[str, str]]:
        """
        获取可用的飞书群组

        Returns:
            [{"group_id": str, "name": str}, ...]
        """
        groups = feishu_service.get_available_groups()
        # 转换格式：从 {id, name} 转为 {group_id, name}
        return [
            {"group_id": g["id"], "name": g["name"]}
            for g in groups
        ]

    def send_to_feishu(
        self,
        title: str,
        content: str,
        group_id: str = "student_union"
    ) -> Dict[str, Any]:
        """
        发送通知到飞书群

        Args:
            title: 通知标题
            content: 通知内容
            group_id: 群组ID

        Returns:
            {"success": bool, "message": str}
        """
        logger.info(f"[Notification] 发送到飞书群: group_id={group_id}")

        # 飞书post消息格式：换行用\n
        feishu_content = content.replace('\n', '\n')

        result = feishu_service.send_post(
            title=title,
            content=feishu_content,
            group_id=group_id
        )

        if result.get("success"):
            logger.info(f"[Notification] 飞书发送成功")
            return {"success": True, "message": "消息发送成功"}
        else:
            error_msg = result.get("error", "发送失败")
            logger.error(f"[Notification] 飞书发送失败: {error_msg}")
            return {"success": False, "message": error_msg}


# 全局单例
notification_service = NotificationService()
