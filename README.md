# AI小商 — 智慧校园AI助手

<div align="center">

基于[讯飞开放平台](https://www.xfyun.cn/)的校园全场景AI助手

[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-4169E1)](https://www.trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-supported-2496ED?logo=docker&logoColor=white)](https://www.docker.com)

</div>

---

## 项目概述

**AI小商** 是一款面向广州商学院师生的智慧校园AI助手，以讯飞开放平台为 AI 能力底座，集成了**星火认知大模型、语音识别（ASR）、语音合成（TTS）、OCR 文字识别、机器翻译、图片理解**等讯飞 API 能力。

项目围绕校园真实场景，构建了覆盖 **学生、教师、管理员** 三端的完整 AI 服务体系——从 AI 对话、课表管理到成绩分析、教案生成，每个模块都将讯飞各项 AI 能力有机结合在校园业务流中。

---

## 功能体系

### 学生端

| 功能模块 | 描述 | 使用的讯飞API |
|----------|------|:---:|
| **AI学姐对话** | 校园知识问答、语音输入/播报、情感陪伴模式、RAG知识库增强 | 星火大模型 · ASR · TTS |
| **智能课表管理** | 拍照OCR导入、图片理解导入、周视图、AI学伴问答、学习建议生成 | OCR · 星火图片理解 · 星火大模型 |
| **录音回顾** | 音频上传 → 异步ASR转写 → AI总结（课程/会议双模式）→ DOCX/PPTX导出 | ASR（文件转写）· 星火大模型 |
| **智能选课助手** | 学生画像雷达图、AI课程推荐、自然语言选课咨询、时间冲突检测 | 星火大模型 |
| **校园活动助手** | AI活动策划方案、多风格宣传文案（5种 × 4种风格）、飞书群推送 | 星火大模型 · 飞书Webhook |
| **日程管理** | 自然语言意图识别（"周二上午9教开会" → 结构化日程） | 星火大模型 |
| **文档翻译** | 文本即时翻译、.txt/.docx文档翻译并下载 | 讯飞机器翻译 |

### 教师端

| 功能模块 | 描述 |
|----------|------|
| **成绩管理** | Excel上传解析、智能权重计算、AI分析报告、成绩导出 |
| **通知生成** | AI撰写面向家长的通知、飞书推送 |
| **教案生成** | AI教学大纲生成、自动制作PPT |

### 管理后台

| 功能模块 | 描述 |
|----------|------|
| **运营看板** | 用户统计、API调用量分析、登录趋势（ECharts） |
| **用户管理** | 用户列表、状态管理、数据导出 |
| **日志审计** | 管理员操作日志、API调用日志、用户行为日志 |

---

## 系统架构

```
┌──────────────────────────────────────────────────────┐
│                     前端展示层                         │
│        Vue.js 3 · Element Plus · Vant · Pinia        │
│                                                      │
│  学生端 (/)  │  教师端 (/teacher)  │  管理端 (/admin)  │
└─────────────────────┬────────────────────────────────┘
                      │  HTTP REST + JWT
┌─────────────────────▼────────────────────────────────┐
│                     后端服务层                         │
│          FastAPI · SQLAlchemy(异步) · Pydantic        │
│                                                      │
│  API路由 (15个模块)  │  业务服务 (15个Service)          │
│                                                      │
│  讯飞API封装: 星火大模型 │ ASR │ TTS │ OCR │ 翻译       │
└─────────────────────┬────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────┐
│                     数据存储层                         │
│     MySQL 8.0 (17个ORM模型) · ChromaDB (RAG向量库)     │
└──────────────────────────────────────────────────────┘
```

---

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js 3 (Composition API) | 3.5.32 | 前端框架 |
| Vite | 8.0.4 | 构建工具 |
| Pinia | 3.0.4 | 状态管理 |
| Vue Router | 4.6.4 | 路由管理 |
| Element Plus | 2.13.7 | PC端UI组件库 |
| Vant | 4.9.24 | 移动端UI组件库 |
| Tailwind CSS | 3.4.0 | 原子化CSS |
| ECharts | 5.6.0 | 数据可视化 |
| Axios | 1.15.0 | HTTP客户端 |
| Playwright | 1.59.1 | E2E测试 |

### 后端

| 技术 | 用途 |
|------|------|
| FastAPI | ASGI Web框架 |
| SQLAlchemy 2.0（异步） | ORM |
| aiomysql | MySQL异步驱动 |
| Pydantic | 数据验证 |
| ChromaDB | 向量数据库（RAG） |
| httpx | 异步HTTP客户端 |
| websocket-client | WebSocket客户端 |
| python-docx / python-pptx | 文档生成 |
| python-jose | JWT认证 |
| ffmpeg（外部依赖） | 音频格式转换 |

### 部署

| 技术 | 用途 |
|------|------|
| MySQL 8.0 | 关系型数据库 |
| ChromaDB | 向量检索（持久化模式） |
| Docker Compose | 三服务编排（MySQL + Backend + Nginx） |
| Nginx | 前端反向代理 |
| JWT (HS256) | 无状态认证 |

---

## 快速开始

### 前置条件

- Python ≥ 3.10
- Node.js ≥ 18
- MySQL ≥ 8.0（或使用 Docker）
- ffmpeg（录音转写音频格式转换需要）

### 1. 配置环境变量

```bash
cp .env.example backend/.env
```

编辑 `backend/.env`，填入讯飞API密钥（从 https://console.xfyun.cn/ 获取）：

```bash
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/ai_xiaoshang
XFYUN_APP_ID=your_app_id
XFYUN_API_KEY=your_api_key
XFYUN_API_SECRET=your_api_secret
SECRET_KEY=change-this-to-random-string
```

### 2. 安装依赖

```bash
# 后端
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 前端
cd ../frontend && npm install
```

### 3. 启动开发服务

```bash
# 终端1：启动后端 → http://localhost:8000
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：启动前端 → http://localhost:5173
cd frontend && npm run dev
```

### 4. Docker 部署

```bash
docker-compose up -d
# 前端: http://localhost
# API文档: http://localhost:8000/docs
```

### 访问入口

| 入口 | 地址 | 说明 |
|------|------|------|
| 学生端 | http://localhost:5173 | AI学姐、课表、录音回顾等 |
| 教师端 | http://localhost:5173/teacher | 成绩管理、通知、教案 |
| 管理端 | http://localhost:5173/admin | 用户管理、运营看板 |
| API文档 | http://localhost:8000/docs | Swagger交互式调试 |

---

## 项目结构

```
AI小商/
├── frontend/src/
│   ├── api/                 # Axios API封装（15个模块）
│   ├── components/          # 可复用Vue组件
│   │   ├── AIBubble.vue         # AI对话气泡
│   │   ├── VoiceInput.vue       # 语音录制按钮
│   │   ├── EmotionToggle.vue    # 情感模式切换
│   │   ├── FileUpload.vue       # 文件上传
│   │   └── course-advisor/      # 选课助手子组件
│   ├── views/               # 页面视图（18个页面）
│   │   ├── Home.vue             # 学生首页
│   │   ├── AISister.vue         # AI学姐对话
│   │   ├── Timetable.vue        # 课表管理
│   │   ├── TimetableImport.vue  # 课表导入
│   │   ├── Review.vue           # 录音回顾
│   │   ├── CourseAdvisor.vue    # 智能选课
│   │   ├── Activity.vue         # 活动助手
│   │   ├── Translate.vue        # 翻译
│   │   ├── teacher/             # 教师端页面（7个）
│   │   └── admin/               # 管理端页面（4个）
│   ├── stores/              # Pinia状态管理（7个模块）
│   ├── router/              # Vue Router（三套路由守卫）
│   ├── layouts/             # 布局组件
│   └── utils/               # 工具函数
│
├── backend/app/
│   ├── main.py              # FastAPI入口（中间件/CORS/异常处理）
│   ├── config.py            # 统一配置管理
│   ├── database.py          # 异步数据库连接池
│   ├── models/              # ORM模型（17个）
│   ├── schemas/             # Pydantic请求/响应模型
│   ├── routers/             # API路由（15个模块）
│   │   ├── chat.py              # AI对话（含RAG/ASR/TTS）
│   │   ├── timetable.py         # 课表管理（OCR导入）
│   │   ├── review.py            # 录音回顾（异步转写+总结）
│   │   ├── course_advisor.py    # 选课助手
│   │   ├── activity.py          # 活动助手 + 飞书推送
│   │   ├── translate.py         # 翻译服务
│   │   ├── export.py            # DOCX/PPTX导出
│   │   ├── teacher/             # 教师端路由
│   │   └── admin_console/       # 管理端路由
│   ├── services/            # 业务服务层（15个Service）
│   │   ├── xinghuo_service.py   # 星火大模型（对话/图片理解/意图识别）
│   │   ├── asr_service.py       # 语音识别（实时流式 + 文件转写）
│   │   ├── tts_service.py       # 语音合成
│   │   ├── ocr_service.py       # OCR识别
│   │   ├── nlp_service.py       # 情感分析
│   │   ├── translation_service.py # 机器翻译
│   │   ├── knowledge_base.py    # ChromaDB RAG知识库
│   │   └── docx_generator.py    # 文档生成
│   └── utils/               # 工具（JWT/异常/日志）
│
├── docs/                    # 项目文档
├── docker-compose.yml       # Docker编排
├── .env.example             # 环境变量模板
└── CLAUDE.md                # 开发规范
```

---

## 讯飞API集成详情

### 实际调用的API

| API名称 | 调用方式 | 应用场景 |
|---------|---------|---------|
| 星火认知大模型 Spark Lite | HTTP POST | AI对话、文本总结、意图识别、情感分析、课表解析、活动策划、教案生成 |
| 星火图片理解 | WebSocket | 课表图片直接识别（端到端图像→结构化数据） |
| 语音听写（流式版） | WebSocket | 实时语音输入（1280字节/40ms分帧） |
| 录音文件转写（大模型版） | HTTP REST | 长音频转写（上传→轮询→获取结果） |
| 在线语音合成 | WebSocket | AI回复语音播报 |
| OCR大模型（通用文档识别） | HTTP POST | 课表图片文字提取 |
| 机器翻译 | HTTP POST | 文本/文档中英互译 |

### 鉴权方式

| 方式 | 使用场景 |
|------|---------|
| Bearer Token | 星火大模型HTTP API |
| HMAC-SHA256 + Base64 URL | 星火图片理解、ASR实时听写、TTS合成、机器翻译 |
| HMAC-SHA256 + Base64 Header | OCR大模型 |
| HMAC-SHA1 参数签名 | 录音文件转写 |

### 工程质量

- **3次自动重试**：所有讯飞API调用支持递增间隔重试（1s → 2s → 3s）
- **API调用全量日志**：记录每次调用的名称、类型、响应时间、错误信息
- **全链路请求追踪**：X-Request-ID 中间件
- **统一异常体系**：`AppException` 四级异常类 + `handle_app_errors` 装饰器
- **异步任务处理**：录音上传后异步转写+总结，不阻塞用户请求
- **ffmpeg音频预处理**：自动转换音频格式适配讯飞API

---

## 架构亮点

1. **清晰的分层架构**：router → service → model 三层分离
2. **异步全链路**：FastAPI ASGI + SQLAlchemy异步 + httpx异步，WebSocket调用通过线程池
3. **RAG增强对话**：ChromaDB向量库 + 校园知识库
4. **双模式课表导入**：OCR + LLM 和 图片理解端到端 互为备份
5. **情感感知对话**：实时分析用户情绪，自动切换心灵陪伴模式
6. **自然语言意图识别**：将对话自动解析为结构化日程
7. **端到端闭环**：录音→转写→AI总结→DOCX/PPTX导出
8. **Docker Compose一键部署**

---

## 已知不足

1. 翻译路由JWT认证未完成（`routers/translate.py` 存在 user_id 硬编码）
2. 两套管理后台路由并存（`routers/admin.py` 旧版 + `routers/admin_console/` 新版）
3. 鉴权代码存在重复（各service独立实现HMAC-SHA256）
4. 测试覆盖不足（2个Playwright测试 + 少量pytest）
5. 缺少Redis缓存层
6. 无CI/CD配置
7. AI Prompt硬编码分散在各service中
8. 教师端功能偏Demo级别
9. 知识库缺少前端管理界面

---

## 相关资源

- [讯飞开放平台](https://www.xfyun.cn/)
- [讯飞控制台（API密钥管理）](https://console.xfyun.cn/)
- [星火大模型](https://xinghuo.xfyun.cn/)
- [ChromaDB文档](https://docs.trychroma.com/)
