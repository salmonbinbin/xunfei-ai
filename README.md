# 讯飞开放平台 API 技术演示仓库

基于[讯飞开放平台](https://www.xfyun.cn/)的多项目技术演示仓库，包含一个完整的智慧校园AI助手全栈应用（**AI小商**）以及多个独立的讯飞API Python演示Demo。

[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-4169E1)](https://www.trychroma.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-supported-2496ED?logo=docker&logoColor=white)](https://www.docker.com)

---

## 仓库结构

```
讯飞项目/
├── AI小商/                          # 【主项目】智慧校园AI助手全栈应用
│   ├── frontend/                    #   Vue.js 3 前端
│   ├── backend/                     #   FastAPI 后端
│   ├── docs/                        #   项目文档
│   ├── websdk-python-demo/          #   讯飞WebSDK完整示例集
│   ├── http_demo/                   #   星火大模型HTTP调用示例
│   ├── docker-compose.yml           #   Docker Compose一键部署
│   └── CLAUDE.md                    #   Claude Code开发规范
│
├── iat_ws_python3_demo/             # 语音听写（流式版）WebSocket Demo
├── Ifasr_llm/                       # 录音文件转写 + 大模型集成 Demo
├── machine_translation_python_demo/ # 机器翻译 HTTP API Demo
├── tts_ws_python3_demo/             # 语音合成 WebSocket API Demo
├── research/                        # 外部采集数据
└── demo.html                        # 产品展示 Landing Page
```

---

## 主项目：AI小商 — 智慧校园AI助手

面向**广州商学院**师生的智慧校园AI助手，以讯飞开放平台为AI能力底座，集成了星火大模型、语音识别、语音合成、OCR、机器翻译等API能力。覆盖学生端、教师端、管理后台三端共11个功能模块。

### 功能一览

#### 学生端

| 功能模块 | 描述 | 使用的讯飞API |
|----------|------|:---:|
| **AI学姐对话** | 校园知识问答、语音输入/播报、情感陪伴模式、RAG知识库增强 | 星火大模型 · ASR · TTS |
| **智能课表管理** | 拍照OCR导入、图片理解导入、周视图展示、AI学伴问答、学习建议生成 | OCR · 星火图片理解 · 星火大模型 |
| **录音回顾** | 音频上传 → 异步ASR转写 → AI智能总结（课程/会议双模式）→ DOCX/PPTX导出 | ASR（文件转写）· 星火大模型 |
| **智能选课助手** | 学生画像雷达图、AI课程推荐、自然语言选课咨询、时间冲突检测 | 星火大模型 |
| **校园活动助手** | AI生成活动策划方案、多风格宣传文案、飞书群组一键推送 | 星火大模型 · 飞书Webhook |
| **日程管理** | 自然语言意图识别创建日程（"周二上午9教开会" → 结构化日程） | 星火大模型 |
| **文档翻译** | 文本即时翻译、.txt/.docx文档上传翻译并下载 | 讯飞机器翻译 |

#### 教师端

| 功能模块 | 描述 | 使用的讯飞API |
|----------|------|:---:|
| **成绩管理** | Excel上传解析、智能权重计算、AI分析报告、成绩导出 | 星火大模型 |
| **通知生成** | AI撰写面向家长的通知、飞书推送 | 星火大模型 · 飞书Webhook |
| **教案生成** | AI教学大纲生成、自动制作PPT | 星火大模型 |

#### 管理后台

| 功能模块 | 描述 |
|----------|------|
| **运营看板** | 用户统计、API调用量分析、登录趋势（ECharts可视化） |
| **用户管理** | 用户列表、状态管理、数据导出 |
| **日志审计** | 管理员操作日志、API调用日志、用户行为日志 |

### 技术栈

**前端：** Vue.js 3.5 + Vite 8 + Pinia 3 + Vue Router 4 + Element Plus 2.13 + Vant 4.9 + Tailwind CSS 3.4 + ECharts 5.6 + Axios

**后端：** FastAPI + SQLAlchemy 2.0（异步） + aiomysql + Pydantic + ChromaDB + httpx + python-docx + python-pptx

**数据库：** MySQL 8.0（24张表）+ ChromaDB（RAG向量检索）

**部署：** Docker Compose（MySQL + Backend + Nginx/Frontend 三服务）

**测试：** Playwright（前端E2E）+ pytest（后端）

### 实际集成的讯飞API

| API名称 | 调用方式 | 实际应用 |
|---------|---------|---------|
| 星火认知大模型 Spark Lite | HTTP POST | AI对话、文本总结、意图识别、情感分析、课表解析、活动策划、教案生成、选课咨询 |
| 星火图片理解 | WebSocket | 课表图片直接识别（端到端图像→结构化数据） |
| 语音听写（流式版） | WebSocket | 实时语音输入识别（40ms/帧） |
| 录音文件转写（大模型版） | HTTP REST | 长音频文件转写（上传→轮询→获取结果） |
| 在线语音合成 | WebSocket | AI回复语音播报（MP3/PCM输出） |
| OCR大模型（通用文档识别） | HTTP POST | 课表图片文字提取 |
| 机器翻译 | HTTP POST | 文本/文档中英互译（支持长文本自动分片） |

> **注意：** NLP情感分析功能并非独立调用讯飞NLP API，而是通过星火大模型配合Prompt Engineering实现，同时保留了关键词匹配fallback方案。

### 快速开始

#### 前置条件

- Python ≥ 3.10
- Node.js ≥ 18
- MySQL ≥ 8.0（或使用Docker）
- ffmpeg（录音转写功能需要音频格式转换）

#### 1. 配置环境变量

```bash
cd AI小商
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

#### 2. 安装依赖

```bash
# 后端
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 前端
cd ../frontend && npm install
```

#### 3. 启动服务

```bash
# 终端1：启动后端 → http://localhost:8000
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：启动前端 → http://localhost:5173
cd frontend && npm run dev
```

#### 4. Docker部署（一键启动）

```bash
docker-compose up -d
# 前端: http://localhost
# API文档: http://localhost:8000/docs
```

### 项目结构

```
AI小商/
├── frontend/src/
│   ├── api/                 # Axios API封装（15个模块）
│   ├── components/          # 可复用Vue组件（AIBubble, VoiceInput, FileUpload等）
│   ├── views/               # 页面视图（学生端/教师端/管理端共18个页面）
│   ├── stores/              # Pinia状态管理（7个模块）
│   ├── router/              # Vue Router（三套路由守卫）
│   ├── layouts/             # 布局组件（MainLayout/AdminLayout/TeacherLayout）
│   └── utils/               # 工具（request拦截器/errorHandler/logger/echarts）
│
├── backend/app/
│   ├── main.py              # FastAPI入口（中间件/异常处理/CORS）
│   ├── config.py            # 统一配置管理
│   ├── database.py          # 异步数据库连接池
│   ├── models/              # ORM模型（17个）
│   ├── schemas/             # Pydantic请求/响应模型
│   ├── routers/             # API路由（15个模块，含学生/教师/管理三端）
│   ├── services/            # 业务服务层（15个Service，含讯飞API封装）
│   └── utils/               # 工具（JWT认证/统一异常/日志）
│
├── docs/                    # 项目文档（Obsidian管理）
└── docker-compose.yml       # Docker编排
```

---

## Demo子项目

### 语音听写（流式版）— `iat_ws_python3_demo/`

讯飞语音听写WebSocket API的Python演示，实现实时语音流式识别。
- WebSocket分帧发送（1280字节/40ms间隔）
- PCM 16kHz 16bit单声道音频
- 完整HMAC-SHA256鉴权实现

### 录音文件转写 — `Ifasr_llm/`

讯飞录音文件转写API的面向对象Python客户端。
- 三阶段流程：上传音频 → 轮询进度 → 获取结果
- 使用Python内置wave模块获取音频时长
- 附带结果解析模块

### 机器翻译 — `machine_translation_python_demo/`

讯飞iTrans机器翻译API的完整调用示例。
- HMAC-SHA256签名鉴权
- 支持自定义术语资源

### 语音合成 — `tts_ws_python3_demo/`

讯飞在线语音合成WebSocket API演示。
- 多发音人支持
- 16000Hz采样率PCM/LAME编码输出

---

## 架构亮点

1. **清晰的分层架构** — router → service → model，职责分明
2. **异步全链路** — FastAPI ASGI + SQLAlchemy异步 + httpx异步HTTP，WebSocket调用通过线程池避免阻塞
3. **统一异常体系** — `AppException` → `NotFoundException`/`ValidationException`/`ThirdPartyException` + 装饰器自动捕获
4. **完善的重试机制** — 所有讯飞API调用支持3次自动重试，间隔递增
5. **RAG增强对话** — ChromaDB向量库 + 校园知识库（15+类FAQ），提升回答针对性
6. **异步任务处理** — 录音上传后通过`asyncio.create_task`异步执行转写+总结，不阻塞用户
7. **双模式课表导入** — OCR文字提取 + 图片理解直接识别，互为备份
8. **自然语言意图识别** — 将"周二上午9点开会"自动解析为结构化日程
9. **情感感知对话** — 实时分析用户情绪，负面情绪自动建议切换"心灵陪伴"模式
10. **全链路日志审计** — API调用日志 + 用户行为日志 + 管理员操作日志 + 登录日志
11. **Docker Compose一键部署** — MySQL + Backend + Nginx三服务编排
12. **E2E测试** — Playwright浏览器端到端测试覆盖核心流程

---

## 已知不足

1. 翻译路由JWT认证未完成（`routers/translate.py`中直接传user_id=1）
2. 两套管理后台路由并存（`routers/admin.py`旧 + `routers/admin_console/`新）
3. 鉴权代码存在重复（每个service独立实现HMAC-SHA256）
4. 缺少Redis缓存层
5. 测试覆盖不足（2个Playwright测试 + 少量pytest）
6. 无CI/CD配置
7. AI Prompt硬编码在service文件中，缺乏集中管理
8. 教师端功能偏Demo级别
9. 知识库缺少前端管理界面
10. 部分TODO标注功能未实现

---

## 相关资源

- [讯飞开放平台](https://www.xfyun.cn/)
- [讯飞控制台（API密钥管理）](https://console.xfyun.cn/)
- [星火大模型](https://xinghuo.xfyun.cn/)
- [讯飞开发文档](https://www.xfyun.cn/doc/)
- [ChromaDB文档](https://docs.trychroma.com/)

---

## License

本项目为技术演示用途，仅供学习、展示和非商业使用。
