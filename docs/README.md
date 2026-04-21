# AI小商 - 项目文档总览

> 所有项目文档的统一入口。本目录下的文档是开发、维护、部署的唯一事实来源。

---

## 📚 文档导航

| 文档 | 内容说明 | 目标读者 |
|-----|---------|---------|
| **[项目规范.md](./项目规范.md)** | 开发规范、错误处理、日志、API设计、数据库规范 | 所有开发者 |
| **[产品需求PRD.md](./产品需求PRD.md)** | 产品愿景、功能需求、用户体验设计 | 产品/全员 |
| **[技术方案.md](./技术方案.md)** | 系统架构、技术选型、部署方案 | 开发者 |
| **[数据库设计.md](./数据库设计.md)** | ER图、表结构、索引设计 | 后端开发者 |
| **[接口规范.md](./接口规范.md)** | API接口定义、请求响应格式 | 前后端开发者 |
| **[前端开发指南.md](./前端开发指南.md)** | 前端项目结构、组件说明、工具函数 | 前端开发者 |
| **[后端开发指南.md](./后端开发指南.md)** | 后端项目结构、服务说明、讯飞API集成 | 后端开发者 |
| **[部署运维.md](./部署运维.md)** | 环境搭建、Docker部署、运维指南 | 运维/开发者 |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd "/Users/salmon/Desktop/Xunfei project/AI小商"

# 后端
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example backend/.env

# 编辑 backend/.env，填入：
# - DATABASE_URL（MySQL连接字符串）
# - XFYUN_APP_ID, XFYUN_API_KEY, XFYUN_API_SECRET（讯飞开放平台）
# - SECRET_KEY（JWT密钥）
```

### 3. 初始化数据库

```bash
cd backend
python scripts/init_db.py
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

### 5. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 📁 项目结构

```
AI小商/
├── docs/                      # 📚 项目文档（本文档目录）
│   ├── README.md              # 文档总览（你在这里）
│   ├── 项目规范.md            # 开发规范
│   ├── 产品需求PRD.md         # 产品需求
│   ├── 技术方案.md            # 技术架构
│   ├── 数据库设计.md          # 数据库设计
│   ├── 接口规范.md            # API接口
│   ├── 前端开发指南.md        # 前端开发
│   ├── 后端开发指南.md        # 后端开发
│   └── 部署运维.md            # 部署运维
│
├── frontend/                  # 🎨 Vue.js 前端
│   ├── src/
│   │   ├── api/              # API 接口封装
│   │   ├── components/       # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态
│   │   ├── router/            # 路由
│   │   └── utils/             # 工具函数
│   └── package.json
│
├── backend/                   # ⚙️ FastAPI 后端
│   ├── app/
│   │   ├── models/           # 数据模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── routers/           # API 路由
│   │   ├── services/         # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── scripts/              # 脚本
│   └── requirements.txt
│
├── nginx/                     # 🌐 Nginx 配置
├── docker-compose.yml         # 🐳 Docker 编排
└── CLAUDE.md                  # 📋 Claude 开发规范
```

---

## 🎯 项目里程碑

| 阶段 | 日期 | 目标 |
|-----|-----|-----|
| Day 1 | 4月13日 | 环境搭建 + 核心架构 |
| Day 2 | 4月14日 | MVP核心功能雏形 |
| Day 3 | 4月15日 | 讯飞ASR/TTS/NLP集成 |
| Day 4 | 4月16日 | 录音回顾全流程打通 |
| Day 5 | 4月17日 | 管理端 + 全流程联调 |
| Day 6 | 4月18日 | 功能完善 + 演示准备 |
| Day 7 | 4月19日 | 最终检查 + 提交 |

---

## 🔗 外部资源

| 资源 | 地址 |
|-----|-----|
| 讯飞开放平台 | https://www.xfyun.cn/ |
| 讯飞控制台 | https://console.xfyun.cn/ |
| 星火大模型体验 | https://xinghuo.xfyun.cn/ |
| 讯飞开发文档 | https://www.xfyun.cn/doc/ |

---

## 📝 文档版本

| 版本 | 日期 | 更新内容 |
|-----|-----|---------|
| v1.0 | 2026-04-13 | 初始版本，整合PRD、技术方案、数据库、接口文档 |

---

> 文档有问题或需要更新？请联系项目维护者。
