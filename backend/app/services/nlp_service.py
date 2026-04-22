"""
NLP情感分析服务

基于讯飞星火大模型的文本情感分析
由于讯飞没有独立的NLP情感分析API，使用星火大模型进行情感分析
"""
import asyncio
import json
import re
from typing import Dict, Any, List
import logging

from app.config import settings
from app.utils.errors import ThirdPartyException
from app.services.xinghuo_service import xinghuo_service

logger = logging.getLogger("xfyun")


class NLPService:
    """NLP情感分析服务类"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    # 情感分析系统提示词
    SENTIMENT_SYSTEM_PROMPT = """你是一个情感分析专家。请分析用户输入文本的情感倾向。

分析规则：
1. positive（积极）: 表达开心、满意、期待、感谢、鼓励等正面情绪
2. negative（消极）: 表达难过、失望、生气、焦虑、恐惧、抱怨等负面情绪
3. neutral（中性）: 陈述事实、询问信息、表达中性观点，无明显情感倾向

置信度规则：
- 情感非常明显且强烈: 0.9-1.0
- 情感较为明显: 0.7-0.9
- 情感有一定倾向但不确定: 0.5-0.7

请严格按以下JSON格式返回，不要返回任何其他内容：
{"sentiment": "positive/neutral/negative", "confidence": 0.0-1.0, "reason": "分析理由（10-30字）"}"""

    def __init__(self):
        self.logger = logging.getLogger("xfyun")

    async def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        情感分析

        Args:
            text: 待分析文本

        Returns:
            情感分析结果:
            {
                "sentiment": "positive/neutral/negative",
                "confidence": 0.95,
                "reason": "分析理由",
                "suggest_emotion_mode": True/False  # 负面情绪时建议切换情感模式
            }
        """
        self.logger.info(f"[NLP] sentiment_analysis called, text: {text[:50]}...")

        if not text or not text.strip():
            self.logger.warning("[NLP] Empty text provided, returning neutral")
            return {
                "sentiment": "neutral",
                "confidence": 1.0,
                "reason": "文本为空",
                "suggest_emotion_mode": False
            }

        try:
            # 构建消息
            messages = [
                {"role": "system", "content": self.SENTIMENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下文本的情感：{text}"}
            ]

            # 调用星火大模型
            response = await xinghuo_service.chat_completion(
                messages=messages,
                user_id="nlp_sentiment",
                temperature=0.3,
                max_tokens=500
            )

            self.logger.debug(f"[NLP] Raw response: {response}")

            # 解析JSON响应
            result = self._parse_sentiment_response(response)

            # 判断是否建议切换情感模式（负面情绪时建议）
            suggest_emotion_mode = result.get("sentiment") == "negative" and result.get("confidence", 0) >= 0.6
            result["suggest_emotion_mode"] = suggest_emotion_mode

            self.logger.info(f"[NLP] Sentiment analysis result: {result}")
            return result

        except ThirdPartyException:
            raise
        except Exception as e:
            self.logger.error(f"[NLP] sentiment_analysis failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="NLP",
                message=f"情感分析失败: {str(e)}",
                original_error=e
            )

    def _parse_sentiment_response(self, response: str) -> Dict[str, Any]:
        """解析星火大模型返回的情感分析结果"""
        try:
            # 尝试直接解析JSON
            result = json.loads(response)
            if "sentiment" in result and "confidence" in result:
                return {
                    "sentiment": result.get("sentiment", "neutral"),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reason": result.get("reason", "")
                }
        except json.JSONDecodeError:
            pass

        # 尝试从文本中提取JSON
        json_match = re.search(r'\{[^{}]*"sentiment"\s*:\s*"(positive|neutral|negative)"[^{}]*"confidence"\s*:\s*([0-9.]+)[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 尝试更宽松的匹配
        sentiment_match = re.search(r'"sentiment"\s*:\s*"(positive|neutral|negative)"', response)
        confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', response)
        reason_match = re.search(r'"reason"\s*:\s*"([^"]*)"', response)

        if sentiment_match and confidence_match:
            return {
                "sentiment": sentiment_match.group(1),
                "confidence": float(confidence_match.group(1)),
                "reason": reason_match.group(1) if reason_match else ""
            }

        # 如果无法解析，返回默认值
        self.logger.warning(f"[NLP] Failed to parse sentiment response: {response[:200]}")
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "reason": "解析失败，默认中性"
        }

    async def batch_sentiment_analysis(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量情感分析

        Args:
            texts: 待分析文本列表

        Returns:
            情感分析结果列表
        """
        self.logger.info(f"[NLP] batch_sentiment_analysis called with {len(texts)} texts")

        results = []
        for text in texts:
            try:
                result = await self.sentiment_analysis(text)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"[NLP] Failed to analyze text: {text[:30]}... Error: {str(e)}")
                results.append({
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "reason": f"分析失败: {str(e)}",
                    "suggest_emotion_mode": False
                })

        return results

    async def sentiment_analysis_with_retry(self, text: str) -> Dict[str, Any]:
        """带重试的情感分析"""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.sentiment_analysis(text)
                self.logger.info(f"[NLP] Sentiment analysis success on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[NLP] Sentiment analysis failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="NLP",
            message="情感分析失败，请稍后重试",
            original_error=last_error
        )

    async def emotion_keywords_analysis(self, text: str) -> Dict[str, Any]:
        """
        基于关键词的情感分析（备用方法，当星火API不可用时使用）

        Args:
            text: 待分析文本

        Returns:
            基于关键词的情感分析结果
        """
        self.logger.info(f"[NLP] emotion_keywords_analysis called")

        # 关键词列表
        positive_keywords = [
            "开心", "高兴", "快乐", "满意", "感谢", "谢谢", "棒", "好", "不错",
            "喜欢", "爱", "期待", "希望", "赞", "优秀", "完美", "太棒了",
            "哈哈", "嘿嘿", "嘻嘻", "欣慰", "兴奋", "激动", "愉快", "幸福"
        ]
        negative_keywords = [
            "难过", "伤心", "失望", "生气", "愤怒", "焦虑", "恐惧", "害怕",
            "讨厌", "恨", "抱怨", "烦", "累", "压力", "紧张", "无奈",
            "唉", "哎", "讨厌", "不爽", "郁闷", "委屈", "痛苦", "崩溃",
            "哭", "泪", "难过", "悲伤", "忧伤", "沮丧", "失落", "绝望"
        ]

        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.5 + positive_count * 0.1, 0.95)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.5 + negative_count * 0.1, 0.95)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "reason": f"关键词匹配: 正面{positive_count}个, 负面{negative_count}个",
            "suggest_emotion_mode": sentiment == "negative" and confidence >= 0.6
        }


# 单例实例
nlp_service = NLPService()
