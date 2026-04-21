"""
星火大模型服务

讯飞开放平台星火认知大模型HTTP API集成
参考: https://www.xfyun.cn/doc/spark/HTTP调用文档.html

模型: Spark Lite
"""
import asyncio
import json
import base64
from typing import List, Dict, Optional, Any
import logging
import httpx
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import ssl
from app.config import settings
from app.utils.errors import ThirdPartyException

logger = logging.getLogger("xfyun")


def generate_websocket_url(api_url: str, api_key: str, api_secret: str) -> str:
    """
    生成星火WebSocket鉴权URL
    参考: https://www.xfyun.cn/doc/spark/general_url_authentication.html
    """
    parsed_url = httpx.URL(api_url)
    host = parsed_url.host
    path = parsed_url.path

    # 生成date (RFC1123格式)
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 签名源
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

    # HMAC-SHA256签名
    import hmac
    import hashlib
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')

    # authorization_origin
    authorization_origin = f"api_key=\"{api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""

    # 编码
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    # 拼接最终URL
    from urllib.parse import quote
    return f"{api_url}?authorization={authorization}&date={quote(date)}&host={host}"


class XingHuoService:
    """星火大模型服务类"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    # API配置 - HTTP方式调用Spark Lite
    API_URL = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    MODEL = "lite"

    def __init__(self):
        self.logger = logging.getLogger("xfyun")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        temperature: float = 0.5,
        max_tokens: int = 4096
    ) -> str:
        """
        聊天补全接口 (HTTP方式)

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            user_id: 用户ID
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的文本内容
        """
        self.logger.info(f"[XingHuo] chat_completion called with {len(messages)} messages, model: {self.MODEL}")

        try:
            # 构造请求头
            headers = {
                "Authorization": f"Bearer {settings.XFYUN_API_PASSWORD}",
                "Content-Type": "application/json"
            }

            # 构造请求体 (兼容OpenAI格式)
            body = {
                "model": self.MODEL,
                "user": user_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            self.logger.debug(f"[XingHuo] Request body: {json.dumps(body, ensure_ascii=False)[:500]}")

            # 发送HTTP请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=body
                )

            self.logger.info(f"[XingHuo] Response status: {response.status_code}")
            self.logger.debug(f"[XingHuo] Response body: {response.text[:1000]}")

            if response.status_code != 200:
                raise ThirdPartyException(
                    service="XingHuo",
                    message=f"星火大模型HTTP请求失败: status={response.status_code}, body={response.text[:500]}",
                    original_error=None
                )

            # 解析响应
            result = response.json()

            # 检查错误码
            code = result.get("code", -1)
            if code != 0:
                error_msg = result.get("message", "未知错误")
                raise ThirdPartyException(
                    service="XingHuo",
                    message=f"星火大模型响应错误: code={code}, message={error_msg}",
                    original_error=None
                )

            # 提取文本内容
            choices = result.get("choices", [])
            if not choices:
                raise ThirdPartyException(
                    service="XingHuo",
                    message="星火大模型返回空choices",
                    original_error=None
                )

            content = choices[0].get("message", {}).get("content", "")
            self.logger.info(f"[XingHuo] Chat success, response length: {len(content)}")
            return content

        except ThirdPartyException:
            raise
        except httpx.TimeoutException:
            raise ThirdPartyException(
                service="XingHuo",
                message="星火大模型请求超时",
                original_error=None
            )
        except Exception as e:
            self.logger.error(f"[XingHuo] Chat failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="XingHuo",
                message=f"星火大模型调用失败: {str(e)}",
                original_error=e
            )

    async def image_understanding(
        self,
        image_data: bytes,
        user_id: str,
        prompt: str = "请识别这张课表图片，提取所有课程信息，包括：课程名称、上课时间（星期、节次）、上课地点、授课老师。以JSON格式返回课程列表。"
    ) -> Dict[str, Any]:
        """
        图片理解接口 (WebSocket方式)

        Args:
            image_data: 图片二进制数据
            user_id: 用户ID
            prompt: 提示词

        Returns:
            解析后的课表数据，包含courses列表
        """
        import websocket

        self.logger.info(f"[XingHuo] image_understanding called, image size: {len(image_data)} bytes")

        API_URL = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"

        # 生成鉴权URL
        ws_url = generate_websocket_url(
            API_URL,
            settings.XFYUN_API_KEY,
            settings.XFYUN_API_SECRET
        )

        # 将图片转为base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 构造WebSocket消息 (按照文档格式)
        request_payload = {
            "header": {
                "app_id": settings.XFYUN_APP_ID,
                "uid": user_id
            },
            "parameter": {
                "chat": {
                    "domain": "general",
                    "temperature": 0.5,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": image_base64,
                            "content_type": "image"
                        },
                        {
                            "role": "user",
                            "content": prompt,
                            "content_type": "text"
                        }
                    ]
                }
            }
        }

        # 使用线程池执行同步WebSocket调用，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        result_text = await loop.run_in_executor(
            None,
            lambda: self._image_understanding_sync(request_payload)
        )

        self.logger.info(f"[XingHuo] Image understanding result length: {len(result_text)}")
        self.logger.info(f"[XingHuo] Raw result: {result_text[:2000]}")

        # 解析JSON结果
        try:
            import re
            # 尝试提取JSON对象
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result_json = json.loads(json_match.group(0))
                # 清理课程名中的节次信息
                if "courses" in result_json and isinstance(result_json["courses"], list):
                    for course in result_json["courses"]:
                        if "name" in course and course["name"]:
                            # 去除课程名末尾的节次信息如 (1-2节)
                            course["name"] = re.sub(r'\s*[\(（【\[【]?\s*\d+[\-－]\d+\s*节?\s*[\)）】\]】]?\s*$', '', course["name"]).strip()
                self.logger.info(f"[XingHuo] Parsed courses: {result_json.get('courses')}")
                return result_json
        except json.JSONDecodeError as e:
            self.logger.warning(f"[XingHuo] Failed to parse image understanding result as JSON: {e}")
            self.logger.warning(f"[XingHuo] Raw result for debug: {result_text}")

        return {"courses": [], "raw_text": result_text}

    def _image_understanding_sync(self, request_payload: Dict) -> str:
        """同步执行图片理解的WebSocket调用"""
        import websocket

        API_URL = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"
        ws_url = generate_websocket_url(
            API_URL,
            settings.XFYUN_API_KEY,
            settings.XFYUN_API_SECRET
        )

        sslopt = {"cert_reqs": ssl.CERT_NONE}
        ws = websocket.create_connection(ws_url, timeout=120, sslopt=sslopt)
        self.logger.info(f"[XingHuo] WebSocket connected")

        try:
            ws.send(json.dumps(request_payload))
            self.logger.info(f"[XingHuo] Request sent")

            result_text = ""
            while True:
                try:
                    msg = ws.recv()
                    if not msg:
                        break

                    data = json.loads(msg)
                    code = data.get("header", {}).get("code", -1)

                    if code != 0:
                        self.logger.error(f"[XingHuo] Error: code={code}, message={data.get('message', '')}")
                        raise ThirdPartyException(
                            service="XingHuo",
                            message=f"图片理解失败: code={code}, message={data.get('message', '')}",
                            original_error=None
                        )

                    # 提取文本内容 (content_type为text或None的assistant回复)
                    text_arr = data.get("payload", {}).get("choices", {}).get("text", [])
                    for item in text_arr:
                        content_type = item.get("content_type")
                        if item.get("role") == "assistant" and (content_type == "text" or content_type is None):
                            result_text += item.get("content", "")

                    # status=2表示最终结果
                    if data.get("header", {}).get("status") == 2:
                        break

                except websocket.WebSocketTimeoutException:
                    self.logger.error("[XingHuo] WebSocket timeout")
                    raise ThirdPartyException(
                        service="XingHuo",
                        message="图片理解超时，请重试",
                        original_error=None
                    )

        finally:
            ws.close()
            self.logger.info(f"[XingHuo] WebSocket closed")

        return result_text

    async def chat_with_retry(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        temperature: float = 0.5,
        max_tokens: int = 4096
    ) -> str:
        """带重试的聊天补全"""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.chat_completion(
                    messages=messages,
                    user_id=user_id,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                self.logger.info(f"[XingHuo] Chat success")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[XingHuo] Chat failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="XingHuo",
            message="星火大模型调用失败，请稍后重试",
            original_error=last_error
        )

    async def text_summary(self, text: str, user_id: str) -> Dict[str, Any]:
        """
        文本总结接口

        Args:
            text: 待总结文本
            user_id: 用户ID

        Returns:
            包含topic, key_points, difficulties, memorable_quote, next_suggestion, full_text的字典
        """
        self.logger.info(f"[XingHuo] text_summary called, text length: {len(text)}")

        prompt = f"""请对以下文本进行总结，提取以下信息：
1. 主题(topic)
2. 核心知识点(key_points)
3. 重点难点(difficulties)
4. 金句(memorable_quote)
5. 预习建议(next_suggestion)
6. 完整文本(full_text)

文本内容：
{text[:8000]}

请以JSON格式返回。"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, user_id, temperature=0.3, max_tokens=2000)

        try:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            self.logger.warning(f"[XingHuo] Failed to parse summary JSON: {e}")

        return {
            "topic": "",
            "key_points": [],
            "difficulties": "",
            "memorable_quote": "",
            "next_suggestion": "",
            "full_text": text[:2000]
        }

    async def intent_recognition(self, text: str, user_id: str) -> Dict[str, Any]:
        """
        自然语言意图识别

        Args:
            text: 用户输入文本（如"周二上午9点去9教开会"）
            user_id: 用户ID

        Returns:
            识别出的意图和参数，包含:
            - event: 事件内容
            - day_of_week: 星期几(1-7)
            - time_desc: 时间描述
            - location: 地点
            - event_type: 事件类型(日程/课程/提醒等)
        """
        self.logger.info(f"[XingHuo] intent_recognition called for: {text[:50]}...")

        try:
            system_prompt = """你是一个日程和课程信息提取助手。请从用户输入的自然语言中提取结构化信息。

支持的格式示例：
- "周二上午9点去9教开会" -> {"event": "开会", "day_of_week": 2, "time_desc": "上午9点", "location": "9教", "event_type": "日程"}
- "周一三五下午2点有高等数学课" -> {"event": "高等数学", "day_of_week": 1, "time_desc": "下午2点", "location": "", "event_type": "课程", "week_days": [1, 3, 5]}
- "周五晚上7点去图书馆" -> {"event": "去图书馆", "day_of_week": 5, "time_desc": "晚上7点", "location": "图书馆", "event_type": "日程"}
- "周三下午3点到5点上体育课" -> {"event": "体育课", "day_of_week": 3, "time_desc": "下午3点到5点", "location": "", "event_type": "课程"}

请严格按照JSON格式返回，只返回JSON，不要有其他内容。字段说明：
- event: 事件/活动名称
- day_of_week: 星期几(1=周一, 2=周二, ..., 7=周日)
- time_desc: 时间描述(保持原表达)
- location: 地点(如果提到)
- event_type: 类型(日程/课程/提醒)
- week_days: 可选，如果是一三五等模式，用数组表示[1,3,5]

只返回JSON！"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]

            response = await self.chat_completion(
                messages=messages,
                user_id=user_id,
                temperature=0.3,
                max_tokens=500
            )

            self.logger.debug(f"[XingHuo] intent_recognition raw response: {response}")

            import re
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    self.logger.info(f"[XingHuo] intent_recognition parsed: {result}")
                    return result
                except json.JSONDecodeError:
                    pass

            return {
                "event": text,
                "day_of_week": None,
                "time_desc": None,
                "location": None,
                "event_type": "日程"
            }

        except ThirdPartyException:
            raise
        except Exception as e:
            self.logger.error(f"[XingHuo] intent_recognition failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="XingHuo",
                message=f"意图识别失败: {str(e)}",
                original_error=e
            )

    async def parse_timetable(self, ocr_text: str) -> List[Dict[str, Any]]:
        """
        解析课表OCR结果，提取课程信息

        Args:
            ocr_text: OCR识别的原始文字

        Returns:
            解析后的课程列表
        """
        import re

        self.logger.info(f"[XingHuo] parse_timetable called, text length: {len(ocr_text)}")

        prompt = TIMETABLE_PARSE_PROMPT.format(ocr_text=ocr_text)
        messages = [{"role": "user", "content": prompt}]

        response = await self.chat_completion(messages, user_id="system", temperature=0.3, max_tokens=4096)

        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            self.logger.warning(f"[XingHuo] Failed to parse timetable JSON: {e}")

        return []

    async def generate_course_insight(self, course_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        为课程生成AI学习建议

        Args:
            course_info: 课程信息，包含name, category, credit

        Returns:
            AI生成的学习建议
        """
        import re

        self.logger.info(f"[XingHuo] generate_course_insight called for: {course_info.get('name')}")

        prompt = COURSE_INSIGHT_PROMPT.format(
            name=course_info.get("name", ""),
            category=course_info.get("category", "专业"),
            credit=str(course_info.get("credit", "未知"))
        )
        messages = [{"role": "user", "content": prompt}]

        response = await self.chat_completion(messages, user_id="system", temperature=0.5, max_tokens=2048)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            self.logger.warning(f"[XingHuo] Failed to parse insight JSON: {e}")

        return {}

    async def chat_about_course(
        self,
        course_id: int,
        question: str,
        course_info: Dict[str, Any]
    ) -> str:
        """
        针对特定课程的AI问答

        Args:
            course_id: 课程ID
            question: 学生问题
            course_info: 课程信息

        Returns:
            AI回答
        """
        self.logger.info(f"[XingHuo] chat_about_course called for course {course_id}: {question[:50]}...")

        prompt = COURSE_CHAT_PROMPT.format(
            name=course_info.get("name", ""),
            category=course_info.get("category", "未知"),
            teacher=course_info.get("teacher", "未知"),
            question=question
        )
        messages = [{"role": "user", "content": prompt}]

        return await self.chat_completion(messages, user_id=str(course_id), temperature=0.7, max_tokens=2048)


# ==================== 课表相关 PROMPT ====================

COURSE_INSIGHT_PROMPT = """你是一个课程学习顾问。请为以下课程生成学习建议：

课程名：{name}
课程类型：{category}（通识/专业/选修）
学分：{credit}

请严格按以下JSON格式返回（只返回JSON，不要其他内容）：
{{
    "course_summary": "课程概述（100字以内）",
    "learning_tips": ["建议1", "建议2", "建议3"],
    "preview_suggestion": "课前预习建议（50字）",
    "review_suggestion": "课后复习建议（50字）",
    "key_points": ["知识点1", "知识点2", "知识点3"],
    "difficulty_level": "easy/medium/hard",
    "importance": "low/medium/high"
}}"""

TIMETABLE_PARSE_PROMPT = """你是一个专业的课表识别助手。请从课表OCR文字中提取课程信息。

返回严格JSON数组格式（**只返回JSON数组，不要任何其他文字！**）：
[
    {
        "name": "课程名称（纯净，不含其他信息）",
        "location": "如九教501、八教505、实训楼402，看不到写null",
        "day_of_week": 1-7数字（1=周一）,
        "start_slot": 1-12数字,
        "end_slot": 1-12数字,
        "week_range": "如1-16周、1-17周，看不到写null"
    }
]

**识别示例：**
- OCR文字"高等数学 九教501 1-2节 1-16周" → name:高等数学, location:九教501, day_of_week:1, start_slot:1, end_slot:2, week_range:1-16周
- OCR文字"大学英语 实训楼402 3-4节" → name:大学英语, location:实训楼402, day_of_week:2, start_slot:3, end_slot:4, week_range:null

**地点格式**：必须是"教学楼+数字"，如九教501、八教505、实训楼402。不是"教室501"也不是"501"。

**节次格式**：如"1-2节"、"3-4节"，对应start_slot=1, end_slot=2"""

COURSE_CHAT_PROMPT = """你是一个课程学习助手。请根据以下课程信息回答学生的问题。

课程名：{name}
课程类型：{category}
授课教师：{teacher}

学生问题：{question}

请用友好、专业的语气回答。如果问题超出课程范围，可以适当扩展。"""


# 单例实例
xinghuo_service = XingHuoService()
