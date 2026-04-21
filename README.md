# AI小商

> 你的智慧校园AI伙伴 — 基于讯飞开放平台的智慧校园AI助手

---

## 项目简介

AI小商是一款面向广州商学院师生的智慧校园AI助手，通过讯飞星火大模型、语音识别、语音合成、OCR识别、NLP情感分析等AI能力，为师生提供：

- 智能课表管家（图片OCR导入 + 自然语言添加日程）
- 课程·会议回顾总结（录音转写 + AI生成总结 + 导出DOCX/PPT）
- AI学姐对话（校园专属问答 + 语音交互 + 情感陪伴模式）
- 智能选课助手
- 校园活动助手

---

## 技术栈

| 层级 | 技术 |
|-----|-----|
| 前端 | Vue.js 3 + Element Plus + Vant |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.0 |
| 向量库 | ChromaDB（RAG知识库） |
| AI能力 | 讯飞开放平台（星火 + ASR + TTS + OCR + NLP） |

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repo-url>
cd AI小商

# 后端依赖
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example backend/.env

# 编辑 backend/.env，填入：
# - DATABASE_URL（MySQL连接）
# - XFYUN_APP_ID, XFYUN_API_KEY, XFYUN_API_SECRET（讯飞开放平台）
# - SECRET_KEY（JWT密钥）
```

### 3. 初始化数据库

```bash
cd backend
mysql -u root -p < scripts/init_db.sql
```

### 4. 启动开发服务器

```bash
# 终端1：后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：前端
cd frontend
npm run dev
```

### 5. 访问

- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## Docker 部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 项目文档

所有项目文档统一在 `docs/` 目录下维护：

| 文档 | 说明 |
|-----|-----|
| [docs/README.md](docs/README.md) | 文档总览与导航 |
| [docs/项目规范.md](docs/项目规范.md) | 开发规范、错误处理、日志 |
| [docs/产品需求PRD.md](docs/产品需求PRD.md) | 产品需求文档 |
| [docs/技术方案.md](docs/技术方案.md) | 系统架构与技术实现 |
| [docs/数据库设计.md](docs/数据库设计.md) | 数据库详细设计 |
| [docs/接口规范.md](docs/接口规范.md) | API接口文档 |
| [docs/前端开发指南.md](docs/前端开发指南.md) | 前端开发规范 |
| [docs/后端开发指南.md](docs/后端开发指南.md) | 后端开发规范 |
| [docs/部署运维.md](docs/部署运维.md) | 部署与运维 |

---

## 讯飞开放平台

| 资源 | 地址 |
|-----|-----|
| 讯飞开放平台 | https://www.xfyun.cn/ |
| 讯飞控制台 | https://console.xfyun.cn/ |
| 星火大模型体验 | https://xinghuo.xfyun.cn/ |
| 开发文档 | https://www.xfyun.cn/doc/ |

---

## 提交物（比赛用）

```
作品压缩包：项目负责人-团队名称-项目名称.zip
  ├── frontend/      # 前端源码
  ├── backend/       # 后端源码
  ├── docs/          # 设计文档
  ├── sql/           # 数据库脚本
  └── README.md      # 运行说明
```

---

## 团队分工

| 角色 | 主要职责 |
|-----|---------|
| 前端负责人 | Vue.js开发、UI设计、组件封装 |
| 后端负责人 | FastAPI开发、讯飞API集成、数据库 |
| 内容/测试 | 知识库内容、文档撰写、测试 |

---

## 开发规范

请阅读 [CLAUDE.md](CLAUDE.md) 了解开发规范，包括：

- 错误处理规范
- 日志记录规范
- API 设计规范
- 数据库规范
- Git 提交规范

---

## 版本

- **v2.0：2026-04-22** - 录音回顾功能全面优化
  - 会议AI摘要质量大幅提升，输出真实内容分析
  - 新增AI摘要重新生成功能
  - 仪表盘统计数据实时显示
  - 录音时长自动获取与显示
  - DOCX/PPTX导出内容优化
- v1.0：2026-04-13 - 项目初始化，完成基础功能

---

## 致谢

- 讯飞开放平台：提供星火大模型及各类AI能力
- 广州商学院：提供比赛平台和场景支持
