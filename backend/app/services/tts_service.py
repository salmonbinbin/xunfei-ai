"""
语音合成(TTS)服务

讯飞开放平台语音合成API集成
参考: https://www.xfyun.cn/doc/tts/online_tts/API.html
"""
import asyncio
import base64
import json
import ssl
import uuid
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import logging
import hashlib
import hmac
import os
from urllib.parse import urlencode

import aiofiles
import websocket

from app.config import settings
from app.utils.errors import ThirdPartyException

logger = logging.getLogger("xfyun")


def generate_tts_url(api_key: str, api_secret: str) -> str:
    """
    生成讯飞TTS WebSocket鉴权URL
    """
    url = "wss://tts-api.xfyun.cn/v2/tts"
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    signature_origin = (
        f"host: tts-api.xfyun.cn\n"
        f"date: {date}\n"
        f"GET /v2/tts HTTP/1.1"
    )

    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    v = {
        "authorization": authorization,
        "date": date,
        "host": "tts-api.xfyun.cn"
    }
    return url + '?' + urlencode(v)


class TTSService:
    """语音合成服务类"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    # 音频格式配置
    AUE_RAW = "raw"
    AUE_LAME = "lame"

    def __init__(self):
        self.logger = logging.getLogger("xfyun")

    def _create_tts_request(self, text: str, voice: str, speed: int, volume: int, pitch: int, aue: str) -> dict:
        """构造TTS请求数据"""
        return {
            "common": {
                "app_id": settings.XFYUN_APP_ID
            },
            "business": {
                "aue": aue,
                "auf": "audio/L16;rate=16000",
                "vcn": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "tte": "utf8"
            },
            "data": {
                "status": 2,
                "text": str(base64.b64encode(text.encode('utf-8')), 'UTF8')
            }
        }

    def _synthesize_sync(self, text: str, voice: str, speed: int, volume: int, pitch: int, aue: str) -> bytes:
        """同步执行TTS WebSocket调用"""
        ws_url = generate_tts_url(settings.XFYUN_API_KEY, settings.XFYUN_API_SECRET)
        sslopt = {"cert_reqs": ssl.CERT_NONE}

        request_data = self._create_tts_request(text, voice, speed, volume, pitch, aue)

        audio_chunks = []
        ws = None

        try:
            ws = websocket.create_connection(ws_url, timeout=30, sslopt=sslopt)
            self.logger.info("[TTS] WebSocket connected")

            ws.send(json.dumps(request_data))
            self.logger.info("[TTS] Request sent, waiting for response...")

            while True:
                try:
                    msg = ws.recv()
                    if not msg:
                        break

                    data = json.loads(msg)
                    code = data.get("code", -1)

                    if code != 0:
                        error_msg = data.get("message", "Unknown error")
                        self.logger.error(f"[TTS] Error: code={code}, message={error_msg}")
                        raise ThirdPartyException(
                            service="TTS",
                            message=f"语音合成失败: code={code}, message={error_msg}",
                            original_error=None
                        )

                    audio = data.get("data", {}).get("audio", "")
                    if audio:
                        audio_chunks.append(base64.b64decode(audio))

                    status = data.get("data", {}).get("status", 0)
                    if status == 2:
                        self.logger.info("[TTS] Synthesis completed")
                        break

                except websocket.WebSocketTimeoutException:
                    self.logger.error("[TTS] WebSocket timeout")
                    raise ThirdPartyException(
                        service="TTS",
                        message="语音合成超时，请重试",
                        original_error=None
                    )

        finally:
            if ws:
                ws.close()
                self.logger.info("[TTS] WebSocket closed")

        if not audio_chunks:
            raise ThirdPartyException(
                service="TTS",
                message="语音合成返回空音频",
                original_error=None
            )

        return b''.join(audio_chunks)

    async def synthesize(
        self,
        text: str,
        voice: str = "xiaoyan",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        audio_format: str = "mp3"
    ) -> bytes:
        """
        文本转语音

        Args:
            text: 待合成文本(最大8000字节约2000汉字)
            voice: 发音人(xiaoyan/aisjiuxu/aisbaby等)
            speed: 语速0-100
            volume: 音量0-100
            pitch: 音调0-100
            audio_format: 音频格式(mp3/pcm)

        Returns:
            音频数据(MP3或PCM格式)
        """
        self.logger.info(f"[TTS] synthesize called, text length: {len(text)}, voice: {voice}, format: {audio_format}")

        # 检查文本长度
        text_bytes = text.encode('utf-8')
        if len(text_bytes) > 8000:
            self.logger.warning(f"[TTS] Text too long ({len(text_bytes)} bytes), truncating to 8000 bytes")
            text = text_bytes[:8000].decode('utf-8', errors='ignore')

        # 选择音频格式
        aue = self.AUE_LAME if audio_format == "mp3" else self.AUE_RAW

        # 使用线程池执行同步WebSocket调用，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        audio_data = await loop.run_in_executor(
            None,
            lambda: self._synthesize_sync(text, voice, speed, volume, pitch, aue)
        )

        self.logger.info(f"[TTS] Synthesis success, audio size: {len(audio_data)} bytes")
        return audio_data

    async def synthesize_to_url(
        self,
        text: str,
        voice: str = "xiaoyan",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50
    ) -> str:
        """
        文本转语音并保存为文件，返回URL

        Args:
            text: 待合成文本
            voice: 发音人
            speed: 语速0-100
            volume: 音量0-100
            pitch: 音调0-100

        Returns:
            音频文件URL
        """
        self.logger.info(f"[TTS] synthesize_to_url called, text length: {len(text)}")

        try:
            # 合成音频
            audio_data = await self.synthesize(
                text=text,
                voice=voice,
                speed=speed,
                volume=volume,
                pitch=pitch,
                audio_format="mp3"
            )

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"tts_{timestamp}_{unique_id}.mp3"

            # 确保目录存在
            upload_dir = os.path.join(settings.UPLOAD_DIR, "tts")
            os.makedirs(upload_dir, exist_ok=True)

            # 保存文件
            file_path = os.path.join(upload_dir, filename)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)

            # 返回URL (相对路径)
            audio_url = f"/uploads/tts/{filename}"
            self.logger.info(f"[TTS] Audio saved to: {file_path}, URL: {audio_url}")

            return audio_url

        except Exception as e:
            self.logger.error(f"[TTS] synthesize_to_url failed: {str(e)}", exc_info=True)
            raise

    async def synthesize_with_retry(
        self,
        text: str,
        voice: str = "xiaoyan",
        speed: int = 50,
        volume: int = 50,
        pitch: int = 50,
        audio_format: str = "mp3"
    ) -> bytes:
        """带重试的语音合成"""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.synthesize(
                    text=text,
                    voice=voice,
                    speed=speed,
                    volume=volume,
                    pitch=pitch,
                    audio_format=audio_format
                )
                self.logger.info(f"[TTS] Synthesis success on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[TTS] Synthesis failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="TTS",
            message="语音合成失败，请稍后重试",
            original_error=last_error
        )


# 单例实例
tts_service = TTSService()
