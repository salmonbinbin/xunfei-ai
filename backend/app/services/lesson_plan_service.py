"""
智能备课教案服务 - 基于讯飞PPT生成API
参考SDK: xfyunsdkspark.ai_ppt.AIPPTClient
"""
import asyncio
import hashlib
import hmac
import base64
import time
import logging
from typing import Dict, Any, Optional, List

import httpx
from app.config import settings
from app.services.xinghuo_service import xinghuo_service

logger = logging.getLogger("lesson_plan_service")


class LessonPlanService:
    """教案服务类"""

    # 讯飞PPT API配置 - 使用正确的域名
    PPT_API_BASE = "https://zwapi.xfyun.cn"
    PPT_THEME_LIST_URL = f"{PPT_API_BASE}/api/ppt/v2/template/list"
    PPT_CREATE_OUTLINE_URL = f"{PPT_API_BASE}/api/ppt/v2/createOutline"
    PPT_CREATE_BY_OUTLINE_URL = f"{PPT_API_BASE}/api/ppt/v2/createPptByOutline"
    PPT_PROCESS_URL = f"{PPT_API_BASE}/api/ppt/v2/progress"

    # 轮询配置
    MAX_POLL_ATTEMPTS = 60
    POLL_INTERVAL = 3

    def __init__(self):
        self.app_id = settings.XFYUN_APP_ID
        self.api_key = settings.XFYUN_API_KEY
        self.api_secret = settings.XFYUN_API_SECRET

    def _generate_signature(self, timestamp: str) -> str:
        """
        生成API签名
        参考: xfyunsdkcore/signature.py Signature.get_signature()
        算法: MD5(app_id + timestamp) -> HMAC-SHA1(api_secret, result) -> Base64
        """
        text = self.app_id + timestamp
        auth = hashlib.md5(text.encode('utf-8')).hexdigest()
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                auth.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        logger.debug(f"[Signature] Generated signature for timestamp={timestamp}")
        return signature

    def _build_headers(self, timestamp: str = None) -> Dict[str, str]:
        """构建请求头（form-data格式，不需要Content-Type）"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        return {
            "appId": self.app_id,
            "timestamp": timestamp,
            "signature": self._generate_signature(timestamp)
        }

    async def _http_post_json(
        self,
        url: str,
        data: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        HTTP POST请求（JSON格式，用于讯飞PPT主题列表等接口）
        """
        timestamp = str(int(time.time()))
        headers = {
            "Content-Type": "application/json",
            "appId": self.app_id,
            "timestamp": timestamp,
            "signature": self._generate_signature(timestamp)
        }

        logger.info(f"[HTTP] POST JSON {url}")
        logger.debug(f"[HTTP] Headers: {headers}, Body: {data}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, headers=headers, json=data)
                    logger.info(f"[HTTP] Response Status: {response.status_code}")

                    result = response.json()
                    logger.info(f"[HTTP] Response: {result}")

                    return result

                except httpx.TimeoutException:
                    logger.warning(f"[HTTP] Timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt == max_retries - 1:
                        raise Exception("讯飞API请求超时")
                except httpx.HTTPStatusError as e:
                    logger.error(f"[HTTP] HTTP Status Error: {e.response.status_code} - {e.response.text[:500]}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"[HTTP] Error: {type(e).__name__}: {str(e)}", exc_info=True)
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))

    async def _http_post_form(
        self,
        url: str,
        data: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        HTTP POST请求（form-data格式，用于讯飞PPT大纲生成等接口）
        参考SDK: xfyunsdkspark.ai_ppt.AIPPTClient.send()
        """
        timestamp = str(int(time.time()))
        headers = self._build_headers()

        logger.info(f"[HTTP] POST form-data {url}")
        logger.debug(f"[HTTP] Headers: {headers}, Body: {data}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(max_retries):
                try:
                    # 使用files参数发送multipart/form-data（httpx会自动设置正确的Content-Type）
                    response = await client.post(url, headers=headers, files=data)
                    logger.info(f"[HTTP] Response Status: {response.status_code}")

                    result = response.json()
                    logger.info(f"[HTTP] Response: {result}")

                    return result

                except httpx.TimeoutException:
                    logger.warning(f"[HTTP] Timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt == max_retries - 1:
                        raise Exception("讯飞API请求超时")
                except httpx.HTTPStatusError as e:
                    logger.error(f"[HTTP] HTTP Status Error: {e.response.status_code} - {e.response.text[:500]}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"[HTTP] Error: {type(e).__name__}: {str(e)}", exc_info=True)
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))

    async def _http_get(self, url: str, max_retries: int = 3, retry_delay: float = 1.0) -> Dict[str, Any]:
        """HTTP GET请求（用于进度查询）"""
        timestamp = str(int(time.time()))
        headers = self._build_headers(timestamp)

        logger.info(f"[HTTP] GET {url}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.get(url, headers=headers)
                    logger.info(f"[HTTP] GET Response Status: {response.status_code}")

                    result = response.json()
                    logger.info(f"[HTTP] GET Response: {result}")

                    return result

                except httpx.TimeoutException:
                    logger.warning(f"[HTTP] GET Timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt == max_retries - 1:
                        raise Exception("讯飞API请求超时")
                except httpx.HTTPStatusError as e:
                    logger.error(f"[HTTP] GET HTTP Status Error: {e.response.status_code} - {e.response.text[:500]}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"[HTTP] GET Error: {type(e).__name__}: {str(e)}", exc_info=True)
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(retry_delay * (attempt + 1))

    async def get_ppt_themes(
        self,
        style: Optional[str] = None,
        color: Optional[str] = None,
        industry: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取PPT主题列表

        Args:
            style: 风格类型（简约/卡通/商务/创意/国风/清新/扁平/插画/节日）
            color: 颜色类型（蓝色/绿色/红色/紫色/黑色/灰色/黄色/粉色/橙色）
            industry: 行业类型
            page: 页码
            page_size: 每页数量

        Returns:
            {"total": int, "records": [...]}
        """
        logger.info(f"[LessonPlan] get_ppt_themes: style={style}, color={color}, industry={industry}")

        data = {
            "pageNum": page,
            "pageSize": page_size
        }
        if style:
            data["style"] = style
        if color:
            data["color"] = color
        if industry:
            data["industry"] = industry

        result = await self._http_post_json(self.PPT_THEME_LIST_URL, data)

        logger.info(f"[LessonPlan] 讯飞API原始返回: {result}")

        # 讯飞PPT API返回 code=0 表示成功，flag可能不存在或为false
        if result.get("code") != 0 and result.get("code") != 200:
            error_desc = result.get('desc', '未知错误')
            logger.error(f"[LessonPlan] 讯飞API返回错误: code={result.get('code')}, desc={error_desc}")
            raise Exception(f"获取PPT主题失败: {error_desc}")

        records = result.get("data", {}).get("records", [])
        # 解析 detailImage JSON字符串，提取 titleCoverImage 作为预览图
        # 同时构造模板名称
        for record in records:
            detail_image = record.get("detailImage", "")
            if detail_image:
                try:
                    import json
                    img_data = json.loads(detail_image)
                    record["detailImage"] = img_data.get("titleCoverImage", "")
                except (json.JSONDecodeError, TypeError):
                    record["detailImage"] = ""

            # 构造模板名称：从 style + industry + color 组合
            parts = []
            if record.get("style"):
                parts.append(record["style"])
            if record.get("industry"):
                parts.append(record["industry"])
            if record.get("color"):
                parts.append(record["color"])
            record["title"] = " ".join(parts) if parts else "未命名模板"

        return {
            "total": result.get("data", {}).get("total", 0),
            "records": records
        }

    async def generate_outline(
        self,
        query: str,
        language: str = "cn",
        search: bool = False
    ) -> Dict[str, Any]:
        """
        生成PPT大纲 - 使用星火大模型

        Args:
            query: 生成要求
            language: 语种（cn/en/ja...）
            search: 是否联网搜索（暂未使用）

        Returns:
            {"sid": str, "outline": {"title": str, "subTitle": str, "chapters": [...]}}
        """
        import re
        import uuid

        logger.info(f"[LessonPlan] generate_outline: query长度={len(query)}")

        # 构建大纲生成prompt
        prompt = self._build_outline_prompt(query)

        try:
            # 调用星火大模型生成大纲
            messages = [{"role": "user", "content": prompt}]
            response = await xinghuo_service.chat_completion(
                messages=messages,
                user_id="lesson_plan",
                temperature=0.7,
                max_tokens=4096
            )

            logger.info(f"[LessonPlan] LLM返回内容长度: {len(response)}")

            # 解析LLM返回的JSON大纲
            outline_data = self._parse_outline_response(response)

            # 生成伪SID用于追踪（LLM生成不需要真实SID）
            sid = f"outline_{uuid.uuid4().hex[:16]}"

            logger.info(f"[LessonPlan] 大纲生成成功: sid={sid}, 章节数={len(outline_data.get('chapters', []))}")

            return {
                "sid": sid,
                "outline": outline_data
            }

        except Exception as e:
            logger.error(f"[LessonPlan] 大纲生成失败: {str(e)}", exc_info=True)
            raise Exception(f"大纲生成失败: {str(e)}")

    def _build_outline_prompt(self, query: str) -> str:
        """
        构建大纲生成的prompt

        Args:
            query: 用户输入的教案相关信息

        Returns:
            完整的prompt字符串
        """
        return f"""请根据以下信息生成一份详细的教学大纲，返回严格的JSON格式。

输入信息：
{query}

请按以下JSON格式返回（只返回JSON，不要其他内容）：
{{
    "title": "教案标题",
    "subTitle": "副标题（可选）",
    "chapters": [
        {{
            "chapterTitle": "第一章标题",
            "chapterContents": ["要点1", "要点2", "要点3"]
        }},
        {{
            "chapterTitle": "第二章标题",
            "chapterContents": ["要点1", "要点2", "要点3"]
        }}
    ]
}}

要求：
1. 章节数量3-5章为宜
2. 每章包含3-5个要点
3. 内容适合高等教育课堂教学
4. 结构清晰，层次分明
5. 只返回JSON，不要任何解释"""

    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM返回的大纲JSON

        Args:
            response: LLM返回的原始文本

        Returns:
            解析后的大纲字典
        """
        import json
        import re

        # 清理markdown格式（LLM常返回```json ... ```）
        cleaned = re.sub(r'^```json\s*', '', response.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned.strip())

        # 尝试提取JSON（查找第一个 { 到最后一个 }）
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if not json_match:
            logger.error(f"[LessonPlan] 无法从响应中提取JSON: {cleaned[:200]}")
            raise ValueError("LLM返回内容不是有效的JSON格式")

        try:
            data = json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}")

        # 验证必要字段
        if "title" not in data:
            raise ValueError("大纲缺少title字段")

        # 确保结构完整
        outline = {
            "title": data.get("title", ""),
            "subTitle": data.get("subTitle"),
            "chapters": []
        }

        # 处理章节数据
        chapters = data.get("chapters", [])
        if isinstance(chapters, list):
            for chapter in chapters:
                if isinstance(chapter, dict) and "chapterTitle" in chapter:
                    outline["chapters"].append({
                        "chapterTitle": chapter.get("chapterTitle", ""),
                        "chapterContents": chapter.get("chapterContents", [])
                    })

        if not outline["chapters"]:
            raise ValueError("大纲缺少有效的章节数据")

        return outline

    def _convert_outline_for_api(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        将LLM生成的大纲转换为讯飞PPT API所需的格式

        LLM返回: chapterContents: ["字符串1", "字符串2"]
        API期望: chapterContents: [{"chapterTitle": "字符串1", "chapterContents": []}, ...]
        """
        api_chapters = []
        for chapter in outline.get("chapters", []):
            # 将字符串列表转换为API期望的对象列表
            api_contents = []
            for content in chapter.get("chapterContents", []):
                if isinstance(content, str):
                    api_contents.append({
                        "chapterTitle": content,
                        "chapterContents": []
                    })
                elif isinstance(content, dict):
                    # 如果已经是对象格式，保留但确保有chapterContents字段
                    api_contents.append({
                        "chapterTitle": content.get("chapterTitle", ""),
                        "chapterContents": content.get("chapterContents", [])
                    })

            api_chapters.append({
                "chapterTitle": chapter.get("chapterTitle", ""),
                "chapterContents": api_contents
            })

        return {
            "title": outline.get("title", ""),
            "subTitle": outline.get("subTitle"),
            "chapters": api_chapters
        }

    def _flatten_outline(self, raw_outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        将讯飞返回的嵌套大纲结构展平

        讯飞返回: {chapterTitle, chapterContents: [{chapterTitle, chapterContents: [...]}, ...]}
        转换后: {title, subTitle, chapters: [{chapterTitle, chapterContents: [字符串, ...]}]}
        """
        chapters = []
        for chapter in raw_outline.get("chapters", []):
            # 提取所有嵌套的chapterTitle作为内容
            contents = []
            for sub in chapter.get("chapterContents", []):
                sub_title = sub.get("chapterTitle", "")
                if sub_title:
                    contents.append(sub_title)
                # 递归提取更深层的内容
                for deep in sub.get("chapterContents", []):
                    deep_title = deep.get("chapterTitle", "")
                    if deep_title:
                        contents.append(deep_title)

            chapters.append({
                "chapterTitle": chapter.get("chapterTitle", ""),
                "chapterContents": contents if contents else []
            })

        return {
            "title": raw_outline.get("title", ""),
            "subTitle": raw_outline.get("subTitle"),
            "chapters": chapters
        }

    async def generate_ppt_by_outline(
        self,
        outline: Dict[str, Any],
        query: str,
        template_id: Optional[str] = None,
        author: str = "AI小商",
        language: str = "cn",
        search: bool = False,
        is_figure: bool = False,
        ai_image: str = "normal",
        is_card_note: bool = False,
        outline_sid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        通过大纲生成PPT

        Args:
            outline: 大纲数据（JSON对象）
            query: 生成要求
            template_id: 模板ID
            author: PPT作者
            language: 语种
            search: 是否联网搜索
            is_figure: 是否AI配图
            ai_image: AI配图类型（normal/advanced）
            is_card_note: 是否生成演讲备注
            outline_sid: 大纲SID（用于关联）

        Returns:
            {"sid": str, "title": str, "ppt_url": str, ...}
        """
        logger.info(f"[LessonPlan] generate_ppt_by_outline: outline有{len(outline.get('chapters', []))}章节")

        # 转换大纲格式：LLM返回的chapterContents是字符串列表，API需要是对象列表
        api_outline = self._convert_outline_for_api(outline)

        data = {
            "query": query,
            "file": None,
            "fileUrl": None,
            "fileName": None,
            "templateId": template_id,
            "businessId": None,
            "author": author,
            "isCardNote": is_card_note,
            "search": search,
            "language": language,
            "isFigure": is_figure,
            "aiImage": ai_image if ai_image else None,
            "outline": api_outline,
            "outlineSid": outline_sid
        }

        result = await self._http_post_json(
            self.PPT_CREATE_BY_OUTLINE_URL,
            data,
            max_retries=3,
            retry_delay=2.0
        )

        logger.info(f"[LessonPlan] PPT生成API返回: {result}")

        # 检查错误码
        code = result.get("code")
        if code != 0 and code != 200:
            error_messages = {
                20005: "大纲生成失败，请检查是否存在敏感词汇",
                20006: "PPT生成失败，请稍后重试或联系技术人员",
                20007: "鉴权错误，请检查讯飞API配置",
            }
            error_msg = error_messages.get(code, f"讯飞API错误: {result.get('desc')}")
            logger.error(f"[LessonPlan] PPT生成失败: code={code}, desc={result.get('desc')}")
            raise Exception(error_msg)

        ppt_data = result.get("data", {})
        logger.info(f"[LessonPlan] PPT生成任务已创建: sid={ppt_data.get('sid')}")

        return {
            "sid": ppt_data.get("sid"),
            "cover_img_src": ppt_data.get("coverImgSrc"),
            "title": ppt_data.get("title"),
            "sub_title": ppt_data.get("subTitle"),
            "outline": ppt_data.get("outline")
        }

    async def poll_ppt_status(self, sid: str) -> Dict[str, Any]:
        """
        轮询PPT生成状态（使用GET请求）

        Args:
            sid: PPT任务ID

        Returns:
            {"ppt_status": str, "ppt_url": str, "total_pages": int, "done_pages": int}
        """
        logger.info(f"[LessonPlan] poll_ppt_status: sid={sid}")

        # GET请求，sid作为URL参数
        url = f"{self.PPT_PROCESS_URL}?sid={sid}"

        for attempt in range(self.MAX_POLL_ATTEMPTS):
            result = await self._http_get(url, max_retries=1)

            logger.info(f"[LessonPlan] 状态查询API返回: {result}")

            # 检查错误码
            if result.get("code") != 0 and result.get("code") != 200:
                raise Exception(f"查询PPT状态失败: {result.get('desc')}")

            ppt_data = result.get("data", {})
            ppt_status = ppt_data.get("pptStatus")

            logger.info(f"[LessonPlan] 状态: {ppt_status}, 完成页数: {ppt_data.get('donePages')}/{ppt_data.get('totalPages')}")

            if ppt_status == "done":
                return {
                    "ppt_status": "completed",
                    "ppt_url": ppt_data.get("pptUrl"),
                    "ai_image_status": ppt_data.get("aiImageStatus"),
                    "card_note_status": ppt_data.get("cardNoteStatus"),
                    "total_pages": ppt_data.get("totalPages"),
                    "done_pages": ppt_data.get("donePages")
                }
            elif ppt_status == "build_failed":
                raise Exception(f"PPT生成失败: {ppt_data.get('errMsg')}")

            await asyncio.sleep(self.POLL_INTERVAL)

        raise Exception("PPT生成超时，请稍后重试")

    def build_lesson_plan_prompt(
        self,
        title: str,
        knowledge_points: str,
        course_name: Optional[str] = None,
        target_audience: Optional[str] = None,
        teaching_hours: Optional[int] = None
    ) -> str:
        """
        构建教案生成Prompt

        Args:
            title: 教案标题
            knowledge_points: 知识点
            course_name: 课程名称
            target_audience: 授课对象
            teaching_hours: 课时数

        Returns:
            生成大纲用的prompt字符串
        """
        prompt = f"""请为以下教学内容生成一份详细的教学大纲：

## 教案标题
{title}

## 课程名称
{course_name or "未指定"}

## 授课对象
{target_audience or "广州商学院学生"}

## 课时数
{teaching_hours or 2}课时

## 核心知识点
{knowledge_points}

请生成一份结构清晰、适合教学的大纲，包含：
1. 封面信息（标题、副标题）
2. 章节结构（每个章节包含章节标题和详细内容要点）
3. 每个章节的内容应该包含3-5个要点

要求：
- 适合高等教育课堂教学
- 内容专业、准确
- 结构层次分明
- 突出重难点"""
        return prompt


# 全局单例
lesson_plan_service = LessonPlanService()