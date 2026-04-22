"""
机器翻译服务

讯飞机器翻译API集成
参考: https://itrans.xf-yun.com
"""
import asyncio
import json
import base64
import time
import logging
import httpx
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from typing import Optional
from app.config import settings
from app.utils.errors import ThirdPartyException

logger = logging.getLogger("xfyun")


def generate_auth_url(api_url: str, api_key: str, api_secret: str) -> dict:
    """
    生成讯飞翻译API鉴权信息
    参考讯飞官方demo实现
    """
    from urllib.parse import urlparse

    parsed_url = urlparse(api_url)
    host = parsed_url.netloc
    path = parsed_url.path

    # 生成date (RFC1123格式)
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 签名源 - 与官方demo一致
    signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"

    # HMAC-SHA256签名
    import hmac
    import hashlib
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')

    # authorization_origin - 与官方demo一致
    authorization_origin = f"api_key=\"{api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""

    # 最终authorization - base64编码
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    return {
        "authorization": authorization,
        "date": date,  # 不需要URL编码
        "host": host
    }


class TranslationService:
    """机器翻译服务类"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [1.0, 2.0, 3.0]  # 递增间隔
    MAX_TEXT_LENGTH = 5000  # 单次翻译最大字符数

    # API配置
    API_URL = "https://itrans.xf-yun.com/v1/its"

    def __init__(self):
        self.logger = logging.getLogger("xfyun")

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        即时翻译文本

        Args:
            text: 待翻译文本
            source_lang: 源语言代码 (如 'cn', 'en', 'ja')
            target_lang: 目标语言代码

        Returns:
            翻译后的文本
        """
        text_length = len(text)
        self.logger.info(
            f"[Translation] Starting translate: text_length={text_length}, "
            f"source={source_lang}, target={target_lang}"
        )

        # 文本长度检查，分片处理
        if text_length > self.MAX_TEXT_LENGTH:
            self.logger.info(
                f"[Translation] Text exceeds {self.MAX_TEXT_LENGTH} chars, "
                f"splitting into chunks"
            )
            return await self._translate_long_text(text, source_lang, target_lang)

        # 单次翻译
        return await self._translate_with_retry(text, source_lang, target_lang)

    async def translate_document(
        self,
        content: str,
        target_lang: str,
        source_lang: str = "auto"
    ) -> str:
        """
        文档翻译

        Args:
            content: 文档文本内容
            target_lang: 目标语言代码
            source_lang: 源语言代码，默认为自动检测

        Returns:
            翻译后的文本
        """
        content_length = len(content)
        self.logger.info(
            f"[Translation] Starting document translate: content_length={content_length}, "
            f"source={source_lang}, target={target_lang}"
        )

        # 文档翻译同样需要分片处理
        if content_length > self.MAX_TEXT_LENGTH:
            self.logger.info(
                f"[Translation] Document exceeds {self.MAX_TEXT_LENGTH} chars, "
                f"splitting into chunks"
            )
            return await self._translate_long_text(content, source_lang, target_lang)

        return await self._translate_with_retry(content, source_lang, target_lang)

    async def _translate_with_retry(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """带重试的翻译调用"""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                start_time = time.time()
                result = await self._do_translate(text, source_lang, target_lang)
                elapsed_ms = int((time.time() - start_time) * 1000)

                self.logger.info(
                    f"[Translation] Translate success: elapsed={elapsed_ms}ms, "
                    f"result_length={len(result)}"
                )
                return result

            except Exception as e:
                last_error = e
                error_msg = str(e)

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    self.logger.warning(
                        f"[Translation] Retrying translate: attempt={attempt + 2}/{self.MAX_RETRIES}, "
                        f"reason={error_msg}, delay={delay}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"[Translation] Translate failed: error={error_msg}, "
                        f"attempt={self.MAX_RETRIES}/{self.MAX_RETRIES}"
                    )

        # 所有重试都失败
        raise ThirdPartyException(
            service="Translation",
            message=f"翻译失败，已重试{self.MAX_RETRIES}次: {str(last_error)}",
            original_error=last_error
        )

    async def _do_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """执行单次翻译请求"""
        # 记录API配置信息（脱敏）
        self.logger.info(
            f"[Translation] API Config: app_id={settings.XFYUN_APP_ID[:4]}***, "
            f"api_key={settings.XFYUN_API_KEY[:4]}***, api_secret={settings.XFYUN_API_SECRET[:4]}***"
        )

        # 生成鉴权信息（包含URL query params）
        auth_params = generate_auth_url(
            self.API_URL,
            settings.XFYUN_API_KEY,
            settings.XFYUN_API_SECRET
        )

        self.logger.info(f"[Translation] Auth params generated: host={auth_params['host']}")

        # 构造请求头 - 与官方demo一致
        headers = {
            "Content-Type": "application/json",
            "host": auth_params["host"]
        }

        # 构建完整的URL（包含鉴权参数作为query string）
        from urllib.parse import urlencode
        full_url = f"{self.API_URL}?{urlencode({
            'authorization': auth_params['authorization'],
            'date': auth_params['date'],
            'host': auth_params['host']
        })}"

        self.logger.info(f"[Translation] Full URL: {full_url[:100]}...")

        # 文本base64编码
        text_base64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')

        # 构造请求体
        request_body = {
            "header": {
                "app_id": settings.XFYUN_APP_ID,
                "status": 3
            },
            "parameter": {
                "its": {
                    "from": source_lang,
                    "to": target_lang,
                    "result": {}
                }
            },
            "payload": {
                "input_data": {
                    "encoding": "utf8",
                    "status": 3,
                    "text": text_base64
                }
            }
        }

        self.logger.info(
            f"[Translation] Request: source={source_lang}, target={target_lang}, "
            f"text_length={len(text)}"
        )

        try:
            self.logger.info("[Translation] Sending request to itrans.xf-yun.com...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    full_url,
                    headers=headers,
                    json=request_body
                )

            self.logger.info(
                f"[Translation] Response received: status={response.status_code}"
            )
            self.logger.debug(
                f"[Translation] Response body: {response.text[:500]}"
            )

            if response.status_code != 200:
                raise ThirdPartyException(
                    service="Translation",
                    message=f"翻译API请求失败: status={response.status_code}, body={response.text[:500]}",
                    original_error=None
                )

            # 解析响应
            result = response.json()

            # 检查讯飞返回的code
            xf_code = result.get("header", {}).get("code", -1)
            if xf_code != 0:
                error_msg = result.get("header", {}).get("message", "未知错误")
                raise ThirdPartyException(
                    service="Translation",
                    message=f"翻译API错误: code={xf_code}, message={error_msg}",
                    original_error=None
                )

            # 提取翻译结果 (base64编码的text字段)
            response_text_base64 = result.get("payload", {}).get("result", {}).get("text", "")
            if not response_text_base64:
                raise ThirdPartyException(
                    service="Translation",
                    message="翻译API返回空结果",
                    original_error=None
                )

            # 解码base64
            decoded_text = base64.b64decode(response_text_base64).decode('utf-8')

            # 解析JSON获取翻译结果
            response_data = json.loads(decoded_text)
            trans_result = response_data.get("trans_result", {})
            dst_text = trans_result.get("dst", "")

            if not dst_text:
                raise ThirdPartyException(
                    service="Translation",
                    message="翻译结果为空",
                    original_error=None
                )

            return dst_text

        except httpx.TimeoutException:
            raise ThirdPartyException(
                service="Translation",
                message="翻译请求超时",
                original_error=None
            )
        except ThirdPartyException:
            raise
        except json.JSONDecodeError as e:
            raise ThirdPartyException(
                service="Translation",
                message=f"翻译响应JSON解析失败: {str(e)}",
                original_error=e
            )
        except Exception as e:
            self.logger.error(f"[Translation] Translate error: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="Translation",
                message=f"翻译失败: {str(e)}",
                original_error=e
            )

    async def _translate_long_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        处理长文本翻译（超过5000字符）

        按照句子/段落分割，分别翻译后拼接
        """
        # 简单按换行符和句号分割
        chunks = self._split_text(text)

        self.logger.info(
            f"[Translation] Split text into {len(chunks)} chunks for long text translation"
        )

        translated_chunks = []
        for i, chunk in enumerate(chunks):
            self.logger.debug(
                f"[Translation] Translating chunk {i + 1}/{len(chunks)}, "
                f"length={len(chunk)}"
            )
            try:
                translated = await self._translate_with_retry(chunk, source_lang, target_lang)
                translated_chunks.append(translated)
            except Exception as e:
                self.logger.warning(
                    f"[Translation] Chunk {i + 1} translation failed, "
                    f"using original text: {str(e)}"
                )
                # 翻译失败时保留原文
                translated_chunks.append(chunk)

        return "".join(translated_chunks)

    def _split_text(self, text: str) -> list:
        """
        将长文本分割为多个小块

        优先按段落分割，其次按句子分割
        """
        # 先尝试按双换行分割（段落）
        paragraphs = text.split("\n\n")

        if len(paragraphs) > 1:
            # 进一步检查每个段落是否超过限制
            result = []
            for para in paragraphs:
                if len(para) <= self.MAX_TEXT_LENGTH:
                    result.append(para)
                else:
                    # 段落仍过长，按句子分割
                    result.extend(self._split_by_sentences(para))
            return result

        # 按句子分割
        return self._split_by_sentences(text)

    def _split_by_sentences(self, text: str) -> list:
        """按句子分割长文本"""
        import re

        # 中英文句号、问号、感叹号分割
        sentence_endings = r'[。！？.?!]'
        sentences = re.split(sentence_endings, text)

        result = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 如果加上当前句子会超过限制，先保存当前chunk
            if len(current_chunk) + len(sentence) + 1 > self.MAX_TEXT_LENGTH:
                if current_chunk:
                    result.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        if current_chunk.strip():
            result.append(current_chunk.strip())

        return result if result else [text]


# 单例实例
translation_service = TranslationService()
