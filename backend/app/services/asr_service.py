"""
语音识别(ASR)服务

讯飞开放平台语音识别API集成：
1. 实时语音听写(流式版) WebSocket API - 用于实时语音识别
2. 录音文件转写 API - 用于长音频文件识别

实时听写参考: https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
录音转写参考: https://office-api-ist-dx.iflyaisol.com

音频格式要求：
- 采样率：16000 Hz
- 声道：单声道
- 编码：16bit PCM
"""
import base64
import hashlib
import hmac
import json
import os
import random
import socket
import ssl
import string
import subprocess
import time
import uuid
import wave
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from time import mktime
import asyncio
import httpx
import logging
import urllib.parse
import websocket

from app.config import settings
from app.utils.errors import ThirdPartyException, ValidationException
from app.services.order_result import parse_order_result

logger = logging.getLogger("xfyun")


# ==================== 实时听写(流式版) WebSocket API ====================

# 帧状态标识
STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

# WebSocket配置
WS_URL = "wss://iat-api.xfyun.cn/v2/iat"
AUDIO_FORMAT = "audio/L16;rate=16000"
AUDIO_ENCODING = "raw"
FRAME_SIZE = 1280  # 16kHz, 16bit, 40ms = 16000 * 16 / 8 * 0.04 = 1280 bytes
FRAME_INTERVAL = 0.04  # 40ms


def generate_auth_url() -> str:
    """
    生成讯飞ASR WebSocket鉴权URL

    签名算法:
    1. signature_origin = "host: iat-api.xfyun.cn\\ndate: {RFC1123时间}\\nGET /v2/iat HTTP/1.1"
    2. signature_sha = HMAC-SHA256(APISecret, signature_origin)
    3. signature = Base64(signature_sha)
    4. authorization_origin = 'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    5. authorization = Base64(authorization_origin)
    """
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    signature_origin = f"host: iat-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"
    signature_sha = hmac.new(
        settings.XFYUN_API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{settings.XFYUN_API_KEY}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    v = {
        "authorization": authorization,
        "date": date,
        "host": "iat-api.xfyun.cn"
    }
    return f"{WS_URL}?{urlencode(v)}"


def parse_asr_response(data: Dict[str, Any]) -> Optional[str]:
    """
    解析ASR响应数据，提取识别文字

    Args:
        data: ASR响应的JSON数据

    Returns:
        识别的文字内容，如果失败返回None
    """
    try:
        code = data.get("code", -1)
        if code != 0:
            error_msg = data.get("message", "未知错误")
            logger.error(f"[ASR] Response error: code={code}, message={error_msg}")
            return None

        result = data.get("data", {}).get("result", {})
        ws = result.get("ws", [])

        if not ws:
            return ""

        text = ""
        for item in ws:
            for cw in item.get("cw", []):
                text += cw.get("w", "")

        return text
    except Exception as e:
        logger.error(f"[ASR] Parse response error: {str(e)}", exc_info=True)
        return None


class ASRService:
    """
    讯飞语音识别服务类

    支持两种识别模式：
    1. 实时语音识别 (recognize_realtime): 通过WebSocket流式接口，适用于实时语音输入
    2. 录音文件转写 (recognize_file): 通过HTTP接口，适用于长音频文件识别
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    API_TIMEOUT = 60.0
    WS_TIMEOUT = 60.0  # WebSocket超时

    # 讯飞录音文件转写API (新版)
    LFASR_HOST = "https://office-api-ist-dx.iflyaisol.com"
    API_UPLOAD = "/v2/upload"
    API_GET_RESULT = "/v2/getResult"

    def __init__(self):
        self.logger = logging.getLogger("xfyun")
        self.app_id = settings.XFYUN_APP_ID
        self.access_key_id = settings.XFYUN_API_KEY
        self.access_key_secret = settings.XFYUN_API_SECRET

    def _generate_random_str(self, length=16):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _get_local_time_with_tz(self) -> str:
        """生成带时区偏移的本地时间（格式：yyyy-MM-dd'T'HH:mm:ss±HHmm，如 +0800）"""
        local_now = datetime.now()
        tz = local_now.astimezone()
        tz_offset = tz.strftime('%z')  # macOS返回 +08:00 格式
        tz_offset = tz_offset.replace(':', '')  # 去掉冒号，变成 +0800 格式
        return f"{local_now.strftime('%Y-%m-%dT%H:%M:%S')}{tz_offset}"

    def _get_wav_duration_ms(self, audio_path: str) -> int:
        """
        用Python内置wave模块获取WAV音频时长（毫秒，整数）
        """
        try:
            with wave.open(audio_path, 'rb') as wav_file:
                n_frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration_ms = int(round(n_frames / sample_rate * 1000))
                return duration_ms
        except wave.Error as e:
            raise Exception(f"WAV文件解析失败：{str(e)}")
        except Exception as e:
            raise Exception(f"获取音频时长失败：{str(e)}")

    def _generate_signature(self, params: Dict[str, str]) -> str:
        """
        生成签名（对key和value都进行url encode后生成baseString）
        """
        sign_params = {k: v for k, v in params.items() if k != "signature"}
        sorted_params = sorted(sign_params.items(), key=lambda x: x[0])

        base_parts = []
        for k, v in sorted_params:
            if v is not None and str(v).strip() != "":
                encoded_key = urllib.parse.quote(k, safe='')
                encoded_value = urllib.parse.quote(str(v), safe='')
                base_parts.append(f"{encoded_key}={encoded_value}")

        base_string = "&".join(base_parts)
        self.logger.debug(f"[ASR] Signature base string: {base_string}")

        hmac_obj = hmac.new(
            self.access_key_secret.encode("utf-8"),
            base_string.encode("utf-8"),
            digestmod="sha1"
        )
        signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")
        self.logger.debug(f"[ASR] Generated signature: {signature}")
        return signature

    def _convert_to_wav(self, audio_path: str) -> str:
        """
        将音频文件转换为WAV格式（16000Hz，单声道，16bit PCM）

        Args:
            audio_path: 原始音频文件路径

        Returns:
            转换后的WAV文件路径
        """
        ext = os.path.splitext(audio_path)[1].lower()

        # 如果已经是wav格式且可能符合要求，先检查
        if ext == '.wav':
            try:
                with wave.open(audio_path, 'rb') as wav_file:
                    rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()
                # 如果符合要求，直接返回
                if rate == 16000 and channels == 1:
                    return audio_path
            except:
                pass

        # 生成临时WAV文件路径
        temp_dir = os.path.dirname(audio_path) or "uploads/audio"
        wav_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_converted.wav")

        # 使用ffmpeg转换
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-acodec', 'pcm_s16le',  # 16bit PCM
            '-ar', '16000',           # 16000Hz采样率
            '-ac', '1',               # 单声道
            wav_path, '-y'
        ]

        self.logger.info(f"[ASR] Converting audio to WAV: {audio_path} -> {wav_path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"[ASR] ffmpeg conversion failed: {error_msg}")
                raise Exception(f"音频格式转换失败: {error_msg}")

            if not os.path.exists(wav_path):
                raise Exception("ffmpeg转换后文件不存在")

            self.logger.info(f"[ASR] Audio converted successfully: {wav_path}")
            return wav_path

        except subprocess.TimeoutExpired:
            raise Exception("音频转换超时")
        except FileNotFoundError:
            raise Exception("ffmpeg未安装，请先安装: brew install ffmpeg")

    # ==================== 实时语音识别(WebSocket流式版) ====================

    async def recognize_realtime(
        self,
        audio_data: bytes,
        language: str = "zh_cn",
        accent: str = "mandarin"
    ) -> str:
        """
        实时语音识别

        通过WebSocket流式接口实时识别语音，返回识别文字。

        Args:
            audio_data: 原始音频数据(PCM 16kHz, 16bit, 单声道)
            language: 语种，如 "zh_cn"(中文), "en_us"(英文)
            accent: 方言，如 "mandarin"(普通话)

        Returns:
            识别的文字内容

        Raises:
            ThirdPartyException: 讯飞API调用失败
            ValidationException: 参数验证失败
        """
        if len(audio_data) == 0:
            raise ValidationException("audio_data cannot be empty")

        self.logger.info(f"[ASR] recognize_realtime called, audio size: {len(audio_data)} bytes")

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self._recognize_realtime_sync(audio_data, language, accent)
                self.logger.info(f"[ASR] recognize success, result length: {len(result)}")
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"[ASR] recognize failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="ASR",
            message=f"语音识别失败，请稍后重试: {str(last_error)}",
            original_error=last_error
        )

    async def _recognize_realtime_sync(
        self,
        audio_data: bytes,
        language: str,
        accent: str
    ) -> str:
        """
        同步执行实时语音识别(在线程池中运行)

        Args:
            audio_data: 音频数据
            language: 语种参数
            accent: 方言参数

        Returns:
            识别文字
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._recognize_websocket(audio_data, language, accent)
        )

    def _recognize_websocket(
        self,
        audio_data: bytes,
        language: str,
        accent: str
    ) -> str:
        """
        通过WebSocket执行实时语音识别

        Args:
            audio_data: 音频数据
            language: 语种
            accent: 方言

        Returns:
            识别文字
        """
        ws_url = generate_auth_url()
        self.logger.debug(f"[ASR] WebSocket URL generated")

        sslopt = {"cert_reqs": ssl.CERT_NONE}
        ws = websocket.create_connection(ws_url, timeout=self.WS_TIMEOUT, sslopt=sslopt)
        self.logger.info(f"[ASR] WebSocket connected")

        try:
            # 状态机: 0=第一帧, 1=中间帧, 2=最后一帧
            status = STATUS_FIRST_FRAME
            offset = 0
            result_text = ""

            while True:
                # 计算本帧数据
                end = min(offset + FRAME_SIZE, len(audio_data))
                frame_data = audio_data[offset:end]

                if status == STATUS_FIRST_FRAME:
                    # 第一帧: 发送common + business + data
                    request_payload = {
                        "common": {
                            "app_id": settings.XFYUN_APP_ID
                        },
                        "business": {
                            "domain": "iat",
                            "language": language,
                            "accent": accent,
                            "vinfo": 1,
                            "eos": 10000
                        },
                        "data": {
                            "status": STATUS_FIRST_FRAME,
                            "format": AUDIO_FORMAT,
                            "encoding": AUDIO_ENCODING,
                            "audio": base64.b64encode(frame_data).decode('utf-8')
                        }
                    }
                    ws.send(json.dumps(request_payload))
                    self.logger.debug(f"[ASR] First frame sent, offset={offset}")
                    status = STATUS_CONTINUE_FRAME

                elif status == STATUS_CONTINUE_FRAME:
                    if offset + FRAME_SIZE >= len(audio_data):
                        # 最后一帧
                        status = STATUS_LAST_FRAME
                        request_payload = {
                            "data": {
                                "status": STATUS_LAST_FRAME,
                                "format": AUDIO_FORMAT,
                                "encoding": AUDIO_ENCODING,
                                "audio": base64.b64encode(frame_data).decode('utf-8')
                            }
                        }
                        ws.send(json.dumps(request_payload))
                        self.logger.debug(f"[ASR] Last frame sent, offset={offset}")
                        break
                    else:
                        # 中间帧
                        request_payload = {
                            "data": {
                                "status": STATUS_CONTINUE_FRAME,
                                "format": AUDIO_FORMAT,
                                "encoding": AUDIO_ENCODING,
                                "audio": base64.b64encode(frame_data).decode('utf-8')
                            }
                        }
                        ws.send(json.dumps(request_payload))
                        offset += FRAME_SIZE

                # 模拟音频采样间隔
                time.sleep(FRAME_INTERVAL)

            # 接收识别结果
            while True:
                try:
                    msg = ws.recv()
                    if not msg:
                        break

                    data = json.loads(msg)
                    self.logger.debug(f"[ASR] Received message: code={data.get('code')}")

                    if data.get("code") != 0:
                        error_msg = data.get("message", "未知错误")
                        raise ThirdPartyException(
                            service="ASR",
                            message=f"语音识别失败: code={data.get('code')}, message={error_msg}",
                            original_error=None
                        )

                    # 解析识别结果
                    text = parse_asr_response(data)
                    if text:
                        result_text += text

                    # 检查是否结束
                    frame_status = data.get("data", {}).get("status", -1)
                    if frame_status == 2:
                        # 引擎返回最终结果
                        self.logger.debug(f"[ASR] Final status received")
                        break

                except websocket.WebSocketTimeoutException:
                    self.logger.error("[ASR] WebSocket timeout")
                    raise ThirdPartyException(
                        service="ASR",
                        message="语音识别超时，请重试",
                        original_error=None
                    )

            return result_text

        finally:
            ws.close()
            self.logger.info(f"[ASR] WebSocket closed")

    # ==================== 录音文件识别(HTTP API) ====================

    async def recognize_file(
        self,
        audio_path: str,
        language: str = "mandarin"
    ) -> Dict[str, Any]:
        """
        录音文件识别（长音频）

        Args:
            audio_path: 音频文件路径 (支持MP3等格式，会自动转换为WAV)
            language: 语种 (mandarin/cantonese/english)

        Returns:
            {"text": "...", "segments": [...]}
        """
        self.logger.info(f"[ASR] recognize_file started, audio_path: {audio_path}, language: {language}")

        if not os.path.exists(audio_path):
            raise ThirdPartyException(
                service="ASR",
                message=f"音频文件不存在: {audio_path}",
                original_error=None
            )

        # 转换为WAV格式（讯飞API只支持WAV）
        wav_path = None
        duration_ms = 0
        try:
            wav_path = self._convert_to_wav(audio_path)

            # 获取音频时长
            try:
                duration_ms = self._get_wav_duration_ms(wav_path)
            except Exception:
                file_size = os.path.getsize(audio_path)
                duration_ms = int(file_size / (16000 * 2) * 1000)

            # 执行转写
            result = await self._transcribe_wav(wav_path)
            result["duration_ms"] = duration_ms

            self.logger.info(f"[ASR] recognize_file completed, text length: {len(result.get('text', ''))}, duration: {duration_ms}ms")
            return result

        except ThirdPartyException:
            raise
        except Exception as e:
            self.logger.error(f"[ASR] recognize_file failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="ASR",
                message=f"录音转写失败: {str(e)}",
                original_error=e
            )
        finally:
            # 清理临时WAV文件（如果是被转换的）
            if wav_path and wav_path != audio_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                    self.logger.debug(f"[ASR] Cleaned up temp WAV file: {wav_path}")
                except Exception as e:
                    self.logger.warning(f"[ASR] Failed to clean up temp file: {e}")

    async def _transcribe_wav(self, wav_path: str) -> Dict[str, Any]:
        """
        转写WAV音频文件

        Args:
            wav_path: WAV文件路径

        Returns:
            {"text": "...", "segments": [...]}
        """
        try:
            # 1. 上传音频文件
            self.logger.info(f"[ASR] Step 1/3: Uploading audio file...")
            order_id = await self._upload_audio(wav_path)
            self.logger.info(f"[ASR] Audio uploaded, order_id: {order_id}")

            # 2. 轮询获取转写进度
            self.logger.info(f"[ASR] Step 2/3: Polling for transcription progress...")
            await self._poll_progress(order_id)
            self.logger.info(f"[ASR] Transcription completed")

            # 3. 获取转写结果
            self.logger.info(f"[ASR] Step 3/3: Fetching transcription result...")
            result = await self._get_result(order_id)
            return result

        except ThirdPartyException:
            raise
        except Exception as e:
            self.logger.error(f"[ASR] _transcribe_wav failed: {str(e)}", exc_info=True)
            raise ThirdPartyException(
                service="ASR",
                message=f"录音转写失败: {str(e)}",
                original_error=e
            )

    async def _upload_audio(self, audio_path: str) -> str:
        """
        上传WAV音频文件到讯飞

        Args:
            audio_path: WAV文件路径

        Returns:
            order_id: 订单ID
        """
        file_size = os.path.getsize(audio_path)
        file_name = os.path.basename(audio_path)
        date_time = self._get_local_time_with_tz()
        signature_random = self._generate_random_str()

        self.logger.info(f"[ASR] Uploading audio file: {file_name}, size: {file_size} bytes")

        # 获取音频时长（毫秒）
        try:
            duration_ms = self._get_wav_duration_ms(audio_path)
        except Exception:
            # 无法获取时长时使用估算值
            duration_ms = int(file_size / (16000 * 2) * 1000)  # 按16kHz 16bit估算

        self.logger.info(f"[ASR] Audio duration: {duration_ms} ms")

        # 构建URL参数
        url_params = {
            "appId": self.app_id,
            "accessKeyId": self.access_key_id,
            "dateTime": date_time,
            "signatureRandom": signature_random,
            "fileSize": str(file_size),
            "fileName": file_name,
            "language": "autodialect",
            "duration": str(duration_ms)
        }

        # 生成签名
        signature = self._generate_signature(url_params)

        # 构建请求头
        headers = {
            "Content-Type": "application/octet-stream",
            "signature": signature
        }

        # 构建最终请求URL
        encoded_params = []
        for k, v in url_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_params.append(f"{encoded_key}={encoded_v}")
        upload_url = f"{self.LFASR_HOST}{self.API_UPLOAD}?{'&'.join(encoded_params)}"

        self.logger.info(f"[ASR] Upload URL: {upload_url[:150]}...")

        # 读取音频文件
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.API_TIMEOUT, verify=False) as client:
                    response = await client.post(
                        url=upload_url,
                        headers=headers,
                        content=audio_data
                    )

                self.logger.debug(f"[ASR] Upload response status: {response.status_code}")

                if response.status_code != 200:
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"上传音频失败: HTTP {response.status_code}, body: {response.text[:500]}",
                        original_error=None
                    )

                result = response.json()
                self.logger.info(f"[ASR] Upload result: {result}")

                # 检查讯飞返回的错误码
                code = result.get("code", "")
                if code != "000000":
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"上传音频失败: code={code}, desc={result.get('descInfo', '')}",
                        original_error=None
                    )

                order_id = result.get("content", {}).get("orderId", "")
                if not order_id:
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"上传音频成功但未获取到orderId: {result}",
                        original_error=None
                    )

                self.logger.info(f"[ASR] Audio uploaded successfully after {attempt + 1} attempt(s)")
                return order_id

            except ThirdPartyException:
                raise
            except httpx.TimeoutException:
                last_error = Exception("上传音频超时")
                self.logger.warning(f"[ASR] Upload attempt {attempt + 1} timeout")
            except Exception as e:
                last_error = e
                self.logger.warning(f"[ASR] Upload attempt {attempt + 1} failed: {str(e)}")

            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="ASR",
            message="上传音频失败，已达最大重试次数",
            original_error=last_error
        )

    async def _poll_progress(self, order_id: str) -> None:
        """
        轮询获取转写进度

        Args:
            order_id: 订单ID
        """
        ts = str(int(time.time()))
        date_time = self._get_local_time_with_tz()
        signature_random = self._generate_random_str()

        query_params = {
            "appId": self.app_id,
            "accessKeyId": self.access_key_id,
            "dateTime": date_time,
            "ts": ts,
            "orderId": order_id,
            "signatureRandom": signature_random
        }

        signature = self._generate_signature(query_params)

        query_headers = {
            "Content-Type": "application/json",
            "signature": signature
        }

        encoded_query_params = []
        for k, v in query_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_query_params.append(f"{encoded_key}={encoded_v}")
        query_url = f"{self.LFASR_HOST}{self.API_GET_RESULT}?{'&'.join(encoded_query_params)}"

        max_retry = 120  # 最多120次轮询 (约20分钟，因为每次sleep 10秒)
        retry_count = 0

        while retry_count < max_retry:
            try:
                await asyncio.sleep(10)  # 每次等待10秒

                async with httpx.AsyncClient(timeout=self.API_TIMEOUT, verify=False) as client:
                    response = await client.post(
                        url=query_url,
                        headers=query_headers,
                        content=json.dumps({})
                    )

                if response.status_code != 200:
                    self.logger.warning(f"[ASR] Query progress failed: HTTP {response.status_code}")
                    retry_count += 1
                    continue

                result = response.json()
                code = result.get("code", "")

                if code != "000000":
                    self.logger.warning(f"[ASR] Query progress error: code={code}")
                    retry_count += 1
                    continue

# 转写状态：3=处理中，4=完成, -1=已提交等待处理
                process_status = result.get("content", {}).get("orderInfo", {}).get("status")
                self.logger.debug(f"[ASR] Polling progress: status={process_status} (attempt {retry_count + 1}/{max_retry})")

                if process_status == 4:
                    self.logger.info("[ASR] Transcription completed successfully")
                    return
                elif process_status == -1:
                    # -1 表示已提交，等待处理，继续轮询
                    self.logger.debug("[ASR] Transcription submitted, waiting...")
                    retry_count += 1
                    continue
                elif process_status not in [3, 4]:
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"转写异常：状态码={process_status}, 描述={result.get('descInfo', '未知错误')}",
                        original_error=None
                    )

            except ThirdPartyException:
                raise
            except Exception as e:
                self.logger.warning(f"[ASR] Polling attempt {retry_count + 1} failed: {str(e)}")
                retry_count += 1

        raise ThirdPartyException(
            service="ASR",
            message="转写超时，未能在规定时间内完成",
            original_error=None
        )

    async def _get_result(self, order_id: str) -> Dict[str, Any]:
        """
        获取转写结果

        Args:
            order_id: 订单ID

        Returns:
            {"text": "...", "segments": [...]}
        """
        ts = str(int(time.time()))
        date_time = self._get_local_time_with_tz()
        signature_random = self._generate_random_str()

        query_params = {
            "appId": self.app_id,
            "accessKeyId": self.access_key_id,
            "dateTime": date_time,
            "ts": ts,
            "orderId": order_id,
            "signatureRandom": signature_random
        }

        signature = self._generate_signature(query_params)

        query_headers = {
            "Content-Type": "application/json",
            "signature": signature
        }

        encoded_query_params = []
        for k, v in query_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_query_params.append(f"{encoded_key}={encoded_v}")
        query_url = f"{self.LFASR_HOST}{self.API_GET_RESULT}?{'&'.join(encoded_query_params)}"

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.API_TIMEOUT, verify=False) as client:
                    response = await client.post(
                        url=query_url,
                        headers=query_headers,
                        content=json.dumps({})
                    )

                if response.status_code != 200:
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"获取转写结果失败: HTTP {response.status_code}",
                        original_error=None
                    )

                result = response.json()
                code = result.get("code", "")

                if code != "000000":
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"获取转写结果失败: code={code}, desc={result.get('descInfo', '')}",
                        original_error=None
                    )

                # 使用orderResult模块解析结果
                text = parse_order_result(result)

                self.logger.info(f"[ASR] Transcription result received, text length: {len(text)}")

                return {
                    "text": text,
                    "segments": []  # 简化处理，只返回完整文本
                }

            except ThirdPartyException:
                raise
            except Exception as e:
                last_error = e
                self.logger.warning(f"[ASR] Get result attempt {attempt + 1} failed: {str(e)}")

            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        raise ThirdPartyException(
            service="ASR",
            message="获取转写结果失败，已达最大重试次数",
            original_error=last_error
        )


# 单例实例
asr_service = ASRService()
