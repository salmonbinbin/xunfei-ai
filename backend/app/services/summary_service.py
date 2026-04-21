"""
AI总结生成服务

基于星火大模型生成课程/会议的結構化总结
参考: docs/产品需求PRD.md 的 F3-2 功能说明
"""
import json
import re
import logging
from typing import Dict, Any, List
from app.services.xinghuo_service import xinghuo_service
from app.utils.errors import ThirdPartyException

logger = logging.getLogger("xfyun")

# ==================== PROMPT 定义 ====================

COURSE_SUMMARY_PROMPT = """你是一个课程学习总结助手。请根据以下录音转写内容，生成结构化的课程总结。

**输出要求：**
请严格按照以下JSON格式返回，不要包含任何其他内容：
```json
{{
    "topic": "课程主题（20字以内）",
    "key_points": "核心知识点（100字以内）",
    "difficulties": "重点难点（80字以内）",
    "memorable_quote": "金句（课程中提到的精彩观点或名言，30字以内）",
    "next_suggestion": "预习建议（60字以内）",
    "full_text": "完整总结文本（200字以内）"
}}
```

**总结原则：**
1. topic：简洁概括课程主题
2. key_points：列出2-4个核心知识点
3. difficulties：识别1-2个重点难点
4. memorable_quote：提取课程中的精彩观点或金句
5. next_suggestion：给出下次课的预习建议
6. full_text：用一段话概括整个课程内容

录音转写内容：
{transcription}

请直接返回JSON，不要有其他解释文字。"""

MEETING_SUMMARY_PROMPT = """你是一个会议记录总结助手。请根据以下录音转写内容，生成结构化的会议总结。

**输出要求：**
请严格按照以下JSON格式返回，不要包含任何其他内容：
```json
{{
    "topic": "会议主题（20字以内）",
    "discussion_points": "讨论要点（100字以内）",
    "resolutions": "决议事项（80字以内）",
    "action_items": "待办事项（60字以内）",
    "full_text": "完整总结文本（150字以内）"
}}
```

**总结原则：**
1. topic：简洁概括会议主题
2. discussion_points：列出主要讨论的问题
3. resolutions：明确会议达成的决议
4. action_items：列出需要执行的后续任务
5. full_text：用一段话概括整个会议内容

录音转写内容：
{transcription}

请直接返回JSON，不要有其他解释文字。"""


class SummaryService:
    """AI总结生成服务类"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self):
        self.logger = logging.getLogger("xfyun")
        self.xinghuo = xinghuo_service

    def _clean_json_response(self, response: str) -> str:
        """清理响应中的markdown代码块标记"""
        # 移除 ```json 和 ``` 标记
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
        return response.strip()

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """从响应中提取JSON对象"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON对象
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError as e:
                self.logger.warning(f"[Summary] JSON parse failed: {e}")
                raise e

        raise ValueError(f"[Summary] Cannot extract JSON from response: {response[:200]}")

    async def generate_course_summary(self, transcription: str, user_id: str = "system") -> Dict[str, Any]:
        """
        生成课程总结

        Args:
            transcription: 录音转写文字
            user_id: 用户ID

        Returns:
            {
                "topic": "主题",
                "key_points": "核心知识点",
                "difficulties": "重点难点",
                "memorable_quote": "金句",
                "next_suggestion": "预习建议",
                "full_text": "完整总结"
            }
        """
        self.logger.info(f"[Summary] generate_course_summary called, transcription length: {len(transcription)}")

        # 构建prompt
        prompt = COURSE_SUMMARY_PROMPT.format(transcription=transcription[:8000])
        self.logger.info(f"[Summary] Course summary prompt length: {len(prompt)}")

        messages = [{"role": "user", "content": prompt}]

        # 调用星火大模型（带重试）
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                self.logger.info(f"[Summary] Calling XingHuo API, attempt {attempt + 1}/{self.MAX_RETRIES}")
                response = await self.xinghuo.chat_completion(
                    messages=messages,
                    user_id=user_id,
                    temperature=0.3,
                    max_tokens=2048
                )
                self.logger.info(f"[Summary] XingHuo response received, length: {len(response)}")

                # 清理响应
                clean_response = self._clean_json_response(response)
                self.logger.debug(f"[Summary] Cleaned response: {clean_response[:500]}")

                # 解析JSON
                result = self._extract_json(clean_response)
                self.logger.info(f"[Summary] Course summary generated: topic={result.get('topic', '')[:30]}...")

                return {
                    "topic": result.get("topic", ""),
                    "key_points": result.get("key_points", ""),
                    "difficulties": result.get("difficulties", ""),
                    "memorable_quote": result.get("memorable_quote", ""),
                    "next_suggestion": result.get("next_suggestion", ""),
                    "full_text": result.get("full_text", "")
                }

            except json.JSONDecodeError as e:
                last_error = e
                self.logger.warning(
                    f"[Summary] JSON parse failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[Summary] Summary generation failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )

            if attempt < self.MAX_RETRIES - 1:
                import asyncio
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        # 所有重试都失败
        self.logger.error(f"[Summary] Course summary generation failed after {self.MAX_RETRIES} attempts")
        raise ThirdPartyException(
            service="XingHuo",
            message="课程总结生成失败，请稍后重试",
            original_error=last_error
        )

    async def generate_meeting_summary(self, transcription: str, user_id: str = "system") -> Dict[str, Any]:
        """
        生成会议总结

        Args:
            transcription: 录音转写文字
            user_id: 用户ID

        Returns:
            {
                "topic": "主题",
                "discussion_points": "讨论要点",
                "resolutions": "决议事项",
                "action_items": "待办事项",
                "full_text": "完整总结"
            }
        """
        self.logger.info(f"[Summary] generate_meeting_summary called, transcription length: {len(transcription)}")

        # 构建prompt
        prompt = MEETING_SUMMARY_PROMPT.format(transcription=transcription[:8000])
        self.logger.info(f"[Summary] Meeting summary prompt length: {len(prompt)}")

        messages = [{"role": "user", "content": prompt}]

        # 调用星火大模型（带重试）
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                self.logger.info(f"[Summary] Calling XingHuo API, attempt {attempt + 1}/{self.MAX_RETRIES}")
                response = await self.xinghuo.chat_completion(
                    messages=messages,
                    user_id=user_id,
                    temperature=0.3,
                    max_tokens=2048
                )
                self.logger.info(f"[Summary] XingHuo response received, length: {len(response)}")

                # 清理响应
                clean_response = self._clean_json_response(response)
                self.logger.debug(f"[Summary] Cleaned response: {clean_response[:500]}")

                # 解析JSON
                result = self._extract_json(clean_response)
                self.logger.info(f"[Summary] Meeting summary generated: topic={result.get('topic', '')[:30]}...")

                return {
                    "topic": result.get("topic", ""),
                    "discussion_points": result.get("discussion_points", ""),
                    "resolutions": result.get("resolutions", ""),
                    "action_items": result.get("action_items", ""),
                    "full_text": result.get("full_text", "")
                }

            except json.JSONDecodeError as e:
                last_error = e
                self.logger.warning(
                    f"[Summary] JSON parse failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[Summary] Summary generation failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )

            if attempt < self.MAX_RETRIES - 1:
                import asyncio
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        # 所有重试都失败
        self.logger.error(f"[Summary] Meeting summary generation failed after {self.MAX_RETRIES} attempts")
        raise ThirdPartyException(
            service="XingHuo",
            message="会议总结生成失败，请稍后重试",
            original_error=last_error
        )

    async def generate_summary(
        self,
        transcription: str,
        record_type: str,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """
        通用总结生成接口

        Args:
            transcription: 录音转写文字
            record_type: 记录类型（"course" 或 "meeting"）
            user_id: 用户ID

        Returns:
            根据record_type返回对应的总结结构
        """
        self.logger.info(f"[Summary] generate_summary called, record_type={record_type}")

        if record_type == "course":
            return await self.generate_course_summary(transcription, user_id)
        elif record_type == "meeting":
            return await self.generate_meeting_summary(transcription, user_id)
        else:
            raise ValueError(f"[Summary] Unknown record_type: {record_type}, expected 'course' or 'meeting'")


# 单例实例
summary_service = SummaryService()