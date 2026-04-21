"""
讯飞OCR识别服务

通用文档识别 (OCR大模型)
参考: https://www.xfyun.cn/doc/words/OCRforLLM/API.html
"""
import base64
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import httpx
import logging
from app.config import settings
from app.utils.errors import ThirdPartyException

logger = logging.getLogger("xfyun")


def generate_ocr_auth_url(api_url: str, api_key: str, api_secret: str) -> Dict[str, str]:
    """
    生成OCR API鉴权URL和header

    返回包含 url, headers 的字典
    """
    from urllib.parse import quote

    parsed_url = httpx.URL(api_url)
    host = parsed_url.host
    path = parsed_url.path

    # 生成date (RFC1123格式)
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 签名源
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

    # authorization_origin
    authorization_origin = f"api_key=\"{api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""

    # 编码
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    # 拼接最终URL
    url = f"{api_url}?authorization={authorization}&date={quote(date)}&host={host}"

    headers = {
        "Content-Type": "application/json",
        "host": host
    }

    return {"url": url, "headers": headers}


class OCRService:
    """讯飞OCR识别服务类"""

    # OCR API地址
    API_URL = "https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm"

    def __init__(self):
        self.logger = logging.getLogger("xfyun")

    async def recognize_document(self, image_data: bytes) -> Dict[str, Any]:
        """
        识别文档图片中的文字

        Args:
            image_data: 图片二进制数据

        Returns:
            识别结果，包含 text 字段
        """
        self.logger.info(f"[OCR] recognize_document called, image size: {len(image_data)} bytes")

        try:
            # 生成鉴权URL和header
            auth = generate_ocr_auth_url(
                self.API_URL,
                settings.XFYUN_API_KEY,
                settings.XFYUN_API_SECRET
            )

            # 将图片转为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 检测图片格式
            if image_data[:8].startswith(b'\x89PNG\r\n\x1a\n'):
                img_encoding = "png"
            elif image_data[:2] == b'\xff\xd8':
                img_encoding = "jpg"
            else:
                img_encoding = "jpg"  # 默认使用jpg

            self.logger.info(f"[OCR] Image encoding: {img_encoding}")

            # 构造请求体
            request_payload = {
                "header": {
                    "app_id": settings.XFYUN_APP_ID,
                    "status": 2  # 结束状态
                },
                "parameter": {
                    "se75ocrbm": {
                        "result_format": "json",
                        "output_type": "one_shot"
                    }
                },
                "payload": {
                    "message": {
                        "image": {
                            "encoding": img_encoding,
                            "image": image_base64,
                            "status": 2
                        }
                    }
                }
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    auth["url"],
                    headers=auth["headers"],
                    json=request_payload
                )

            self.logger.info(f"[OCR] Response status: {response.status_code}")
            self.logger.info(f"[OCR] Response body: {response.text[:500]}")

            if response.status_code != 200:
                raise ThirdPartyException(
                    service="OCR",
                    message=f"OCR请求失败: status={response.status_code}",
                    original_error=None
                )

            result = response.json()
            self.logger.debug(f"[OCR] Response body: {json.dumps(result, ensure_ascii=False)[:500]}")

            # 检查错误码
            code = result.get("header", {}).get("code", -1)
            if code != 0:
                error_msg = result.get("header", {}).get("message", "未知错误")
                raise ThirdPartyException(
                    service="OCR",
                    message=f"OCR识别失败: code={code}, message={error_msg}",
                    original_error=None
                )

            # 解析结果
            text_data = result.get("payload", {}).get("result", {}).get("text", "")
            if text_data:
                # 解码base64
                text = base64.b64decode(text_data).decode('utf-8')
            else:
                text = ""

            self.logger.info(f"[OCR] Recognition success, text length: {len(text)}")

            return {
                "text": text,
                "sid": result.get("header", {}).get("sid", "")
            }

        except ThirdPartyException:
            raise
        except httpx.TimeoutException:
            raise ThirdPartyException(
                service="OCR",
                message="OCR识别超时，请重试",
                original_error=None
            )
        except Exception as e:
            self.logger.error(f"[OCR] Recognition failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="OCR",
                message=f"OCR识别失败: {str(e)}",
                original_error=e
            )


# 单例实例
ocr_service = OCRService()
