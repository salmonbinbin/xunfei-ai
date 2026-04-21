"""
语音识别(ASR)服务

讯飞开放平台录音文件转写API集成
参考: https://office-api-ist-dx.iflyaisol.com

讯飞API要求：
- 音频格式：WAV (PCM)
- 采样率：16000 Hz
- 声道：单声道
- 编码：16bit PCM
"""
import base64
import hmac
import hashlib
import json
import os
import uuid
import time
import random
import string
import subprocess
import wave
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import httpx
import logging
import urllib.parse

from app.config import settings
from app.utils.errors import ThirdPartyException
from app.services.order_result import parse_order_result

logger = logging.getLogger("xfyun")


class ASRService:
    """讯飞录音文件转写服务类"""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    API_TIMEOUT = 60.0

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

                # 转写状态：3=处理中，4=完成
                process_status = result.get("content", {}).get("orderInfo", {}).get("status")
                self.logger.debug(f"[ASR] Polling progress: status={process_status} (attempt {retry_count + 1}/{max_retry})")

                if process_status == 4:
                    self.logger.info("[ASR] Transcription completed successfully")
                    return
                elif process_status not in [3, 4]:
                    raise ThirdPartyException(
                        service="ASR",
                        message=f"转写异常：状态码={process_status}, 描述={result.get('descInfo', '未知错误')}",
                        original_error=None
                    )

                retry_count += 1

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
