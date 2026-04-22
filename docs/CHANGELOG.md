# 更新日志

所有重要的版本更新都会记录在此文件中。

---

## [v2.1.0] - 2026-04-22

### 新增功能

#### 智能翻译
- **即时翻译**：输入中文文本，实时翻译为 8 种语言（英文、日文、韩文、法文、德文、西班牙文、俄文、阿拉伯文）
- **文档翻译**：上传 txt/docx 文件，翻译后可预览并下载 Word 文档
- **技术特性**：
  - 讯飞机器翻译 API 集成
  - HMAC-SHA256 鉴权
  - 3 次自动重试机制
  - 长文本自动分片（>5000 字符）

### 代码变更

| 类型 | 文件 | 变更 |
|-----|------|------|
| 新增 | `backend/app/models/translation.py` | 翻译任务数据模型 |
| 新增 | `backend/app/routers/translate.py` | 翻译 API 路由（4个接口） |
| 新增 | `backend/app/services/translation_service.py` | 讯飞翻译服务层 |
| 新增 | `frontend/src/api/translate.js` | 前端 API 封装 |
| 新增 | `frontend/src/views/Translate.vue` | 翻译功能页面 |
| 修改 | `frontend/src/layouts/MainLayout.vue` | 导航栏添加"智能翻译"入口 |
| 修改 | `frontend/src/views/Home.vue` | 首页添加翻译快捷入口 |
| 修改 | `frontend/src/router/index.js` | 添加 /translate 路由 |

### 数据库变更

```sql
CREATE TABLE translation_tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task_id VARCHAR(64) UNIQUE NOT NULL,
  user_id INT NOT NULL,
  task_type VARCHAR(20) NOT NULL,
  source_lang VARCHAR(10) NOT NULL,
  target_lang VARCHAR(10) NOT NULL,
  original_content TEXT,
  translated_content TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  word_count INT DEFAULT 0,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_task_id (task_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## [v2.0.0] - 2026-04-21

### 新增功能

- AI 学姐智能对话
- 课表 OCR 识别导入
- 录音回顾与转写
- 讯飞语音交互（ASR/TTS）
- ChromaDB 知识库问答

### 主要技术栈

- 前端：Vue.js 3 + Element Plus + Vite
- 后端：FastAPI + SQLAlchemy (async)
- AI：讯飞星火大模型 + 机器翻译 + ASR/TTS
- 数据库：MySQL + ChromaDB
