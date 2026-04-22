"""
飞书 Webhook 服务模块

支持多群配置、富文本消息发送、重试机制
"""
import requests
import logging
import time
from typing import Dict, Any, Optional, List

logger = logging.getLogger("feishu")


class FeishuService:
    """飞书 Webhook 服务类（单例模式）"""

    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 3]  # 递增间隔：1s, 2s, 3s

    # 默认群组配置
    DEFAULT_GROUPS = {
        "student_union": {
            "name": "学生会通知",
            "webhook_env": "FEISHU_WEBHOOK_STUDENT_UNION"
        },
        "club_alliance": {
            "name": "社团联盟",
            "webhook_env": "FEISHU_WEBHOOK_CLUB_ALLIANCE"
        },
        "class_group": {
            "name": "班级通知",
            "webhook_env": "FEISHU_WEBHOOK_CLASS_GROUP"
        },
        "youth_union": {
            "name": "团委通知",
            "webhook_env": "FEISHU_WEBHOOK_YOUTH_UNION"
        },
        "dormitory": {
            "name": "宿舍管理",
            "webhook_env": "FEISHU_WEBHOOK_DORMITORY"
        }
    }

    _instance: Optional["FeishuService"] = None

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, webhooks: Optional[Dict[str, str]] = None):
        """
        初始化飞书服务

        Args:
            webhooks: 群名称到 Webhook URL 的映射，如未提供则从环境变量读取
        """
        if self._initialized:
            return

        self._initialized = True
        self._headers = {"Content-Type": "application/json"}
        self._webhooks: Dict[str, str] = {}
        self._groups_loaded = False

    def _ensure_webhooks_loaded(self):
        """确保webhooks已加载（延迟加载）"""
        if not self._groups_loaded:
            self._webhooks = self._load_webhooks_from_env()
            self._groups_loaded = True
            logger.info(f"[Feishu] Loaded {len(self._webhooks)} groups from environment")

    def _load_webhooks_from_env(self) -> Dict[str, str]:
        """从环境变量加载飞书群配置"""
        import os
        from dotenv import load_dotenv

        # 确保 .env 文件被加载
        load_dotenv('.env')

        webhooks = {}

        for group_id, config in self.DEFAULT_GROUPS.items():
            webhook_url = os.environ.get(config["webhook_env"])
            if webhook_url:
                webhooks[group_id] = webhook_url
            else:
                logger.warning(f"[Feishu] {config['webhook_env']} not set for group: {group_id}")

        return webhooks

    def get_available_groups(self) -> List[Dict[str, str]]:
        """
        获取所有可用的群组列表

        Returns:
            群组信息列表，包含 id, name
        """
        self._ensure_webhooks_loaded()
        return [
            {"id": group_id, "name": config["name"], "configured": group_id in self._webhooks}
            for group_id, config in self.DEFAULT_GROUPS.items()
        ]

    def send_post(
        self,
        title: str,
        content: str,
        group_id: str = "student_union"
    ) -> Dict[str, Any]:
        """
        发送富文本消息到指定群组

        Args:
            title: 消息标题
            content: 消息内容（支持换行 \n）
            group_id: 群组标识，默认为 student_union

        Returns:
            发送结果 {"success": bool, "message": str, "error": str}
        """
        self._ensure_webhooks_loaded()
        webhook_url = self._webhooks.get(group_id)
        if not webhook_url:
            error_msg = f"未找到群组配置: {group_id}"
            logger.error(f"[Feishu] {error_msg}")
            return {"success": False, "error": error_msg}

        # 构造富文本消息
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content}
                            ]
                        ]
                    }
                }
            }
        }

        return self._send_with_retry(webhook_url, payload, group_id)

    def send_text(self, text: str, group_id: str = "student_union") -> Dict[str, Any]:
        """
        发送文本消息到指定群组

        Args:
            text: 消息内容
            group_id: 群组标识

        Returns:
            发送结果
        """
        self._ensure_webhooks_loaded()
        webhook_url = self._webhooks.get(group_id)
        if not webhook_url:
            error_msg = f"未找到群组配置: {group_id}"
            logger.error(f"[Feishu] {error_msg}")
            return {"success": False, "error": error_msg}

        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }

        return self._send_with_retry(webhook_url, payload, group_id)

    def _send_with_retry(
        self,
        webhook_url: str,
        payload: Dict,
        group_id: str
    ) -> Dict[str, Any]:
        """
        带重试的发送请求

        Args:
            webhook_url: Webhook 地址
            payload: 请求体
            group_id: 群组标识（用于日志）

        Returns:
            发送结果
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"[Feishu] Sending to {group_id} (attempt {attempt + 1}/{self.MAX_RETRIES})"
                )

                response = requests.post(
                    webhook_url,
                    headers=self._headers,
                    json=payload,
                    timeout=10
                )

                result = response.json()

                # 检查飞书返回的错误码
                code = result.get("code", result.get("StatusCode", -1))
                if code == 0:
                    logger.info(f"[Feishu] Message sent to {group_id} successfully")
                    return {"success": True, "message": "消息发送成功"}

                # 非零错误码
                error_msg = result.get("msg", result.get("message", f"code={code}"))
                logger.warning(
                    f"[Feishu] Send failed to {group_id} (attempt {attempt + 1}): {error_msg}"
                )
                last_error = Exception(error_msg)

            except requests.exceptions.Timeout:
                error_msg = "请求超时"
                logger.warning(
                    f"[Feishu] Timeout to {group_id} (attempt {attempt + 1}/{self.MAX_RETRIES})"
                )
                last_error = Exception(error_msg)

            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                logger.warning(
                    f"[Feishu] Request error to {group_id} (attempt {attempt + 1}): {error_msg}"
                )
                last_error = e

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"[Feishu] Unexpected error to {group_id} (attempt {attempt + 1}): {error_msg}",
                    exc_info=True
                )
                last_error = e

            # 非最后一次重试，等待递增间隔
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[attempt]
                logger.info(f"[Feishu] Retrying to {group_id} in {delay}s...")
                time.sleep(delay)

        # 所有重试都失败
        final_error = f"发送到{group_id}失败，已重试{self.MAX_RETRIES}次"
        logger.error(f"[Feishu] {final_error}: {last_error}")
        return {"success": False, "error": final_error}


# 单例实例
feishu_service = FeishuService()
