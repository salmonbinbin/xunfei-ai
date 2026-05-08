# AI小商 学生&教师端功能详细文档

> 本文档详细介绍AI小商项目的学生端和教师端所有功能模块、技术实现、API规范等内容。
> 版本：1.0
> 更新日期：2026年5月8日

---

## 一、项目概述

### 1.1 产品定位

**AI小商 — 你的智慧校园AI伙伴**

AI小商是一款基于讯飞开放平台打造的智慧校园AI助手，通过自然语言对话、语音交互、多模态识别等AI能力，一站式解决师生的校园生活、学习、办公需求。

### 1.2 核心价值

| 用户角色 | 核心价值 |
|---------|---------|
| 学生 | 省时间：减少多系统切换；有个性：AI记住你的偏好 |
| 教师 | 省时：AI自动处理繁琐的行政工作；智能：基于大模型生成高质量教学内容 |
| 学校 | 减轻行政咨询压力；积累数字化经验 |
| 比赛 | 最大化讯飞API集成度；完整闭环展示 |

### 1.3 技术栈

| 层级 | 技术 | 说明 |
|-----|------|------|
| 前端框架 | Vue.js 3 + Vite | 渐进式框架 |
| 前端UI | Element Plus + Vant | PC端+移动端组件库 |
| 状态管理 | Pinia | Vue3官方推荐 |
| 后端框架 | FastAPI | 异步高性能框架 |
| 数据库 | MySQL 8.0 | 关系型存储 |
| 向量数据库 | ChromaDB | RAG知识库 |
| AI能力 | 讯飞开放平台 | 全能力集成 |
| 文档生成 | python-docx + python-pptx | DOCX/PPTX生成 |

### 1.4 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户层                                    │
│  ┌──────────────────┐           ┌──────────────────┐          │
│  │   PC浏览器        │           │   手机浏览器      │          │
│  │   (Chrome/Edge)  │           │   (微信/ Safari) │          │
│  └────────┬─────────┘           └────────┬─────────┘          │
└───────────┼───────────────────────────────┼────────────────────┘
            │                               │
            └───────────────┬───────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                      Nginx 反向代理                              │
│              80/443端口 │ SSL终止 │ 静态资源                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
┌───────────▼───────────┐       ┌───────────▼───────────┐
│     Vue.js 前端        │       │    FastAPI 后端       │
│                       │       │   (localhost:8000)    │
│  ┌─────────────────┐  │       │                       │
│  │  Pinia 状态管理  │  │       │  ┌─────────────────┐  │
│  │  Vue Router     │  │       │  │  API Routes     │  │
│  │  Axios HTTP     │  │       │  └────────┬────────┘  │
│  └─────────────────┘  │       │           │            │
│                       │       │  ┌────────▼────────┐  │
│  ┌─────────────────┐  │       │  │  Services层    │  │
│  │  讯飞WebSocket  │◄─┼───────┼──│  xinghuo        │  │
│  │  (ASR实时识别)  │  │       │  │  asr/tts/ocr   │  │
│  └─────────────────┘  │       │  │  nlp/nlp       │  │
│                       │       │  │  docx/pptx     │  │
│                       │       │  │  knowledge_base│  │
│                       │       │  └────────┬────────┘  │
└───────────────────────┼───────┘           │            │
                            │       ┌───────▼────────┐   │
                            │       │   MySQL 8.0    │   │
                            │       └────────────────┘   │
                            │       ┌────────────────┐   │
                            │       │   ChromaDB     │   │
                            │       │   (RAG向量库)   │   │
                            │       └────────────────┘   │
                            │       ┌────────────────┐   │
                            │       │   讯飞开放平台  │   │
                            │       │  星火+ASR+TTS  │   │
                            │       │  OCR+NLP       │   │
                            │       └────────────────┘   │
```

---

## 二、学生端功能

### 2.1 功能总览

| 功能 | 说明 | 优先级 | 状态 |
|-----|-----|-------|-----|
| 登录注册 | 微信扫码/手机号登录 | P0 | ✅ 已完成 |
| 智能课表管家 | 图片OCR导入 + 自然语言添加日程 + 首页提醒 | P0 | ✅ 已完成 |
| 课程·会议回顾 | MP3上传 → ASR转写 → 星火总结 → 导出DOCX/PPT | P0 | ✅ 已完成 |
| AI学姐对话 | 校园专属问答 + 语音输入/播报 + 情感陪伴模式 | P0 | ✅ 已完成 |
| 智能翻译 | 即时翻译（多语言）+ 文档翻译（txt/docx → Word导出） | P1 | ✅ 已完成 |
| 智能选课助手 | 专业+规划 → AI推荐选课 | P1 | ✅ 已完成 |
| 校园活动助手 | AI生成活动策划/宣传文案 + 飞书群推送 | P1 | ✅ 已完成 |

### 2.2 登录注册

#### 2.2.1 功能描述

用户通过手机号注册/登录，完善个人信息后进入首页。

#### 2.2.2 页面路径

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 登录页 | /login | 手机号登录 |
| 引导页 | /guide | 首次登录完善信息 |

#### 2.2.3 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| nickname | string | 用户昵称 |
| openid | string | 微信OpenID（可选） |
| phone | string | 手机号 |
| major | string | 专业 |
| grade | string | 年级 |
| goal | string | 学习目标 |

### 2.3 智能课表管家

#### 2.3.1 课表图片导入（OCR）

**功能流程：**
```
用户上传课表图片
    ↓
讯飞OCR识别 → 获取图片文字
    ↓
讯飞星火大模型解析 → 转为结构化课程数据
    ↓
用户确认 → 写入MySQL courses表
```

**技术实现：**
- 讯飞OCR API识别图片文字
- 星火大模型解析课程信息
- 支持手动调整课程信息

#### 2.3.2 自然语言添加日程

**功能流程：**
```
"周二上午9点去9教开会"
    ↓
星火大模型解析意图
    ↓
提取：时间、地点、事项
    ↓
写入数据库 schedules表
```

#### 2.3.3 首页今日提醒

**功能说明：**
- 今明两日课程醒目展示
- AI学习建议推送

### 2.4 课程·会议回顾

#### 2.4.1 录音转写

**功能流程：**
```
上传MP3（≤50MB）
    ↓
选择类型（课程/会议）
    ↓
讯飞ASR录音文件识别 → 轮询获取转写结果
```

#### 2.4.2 AI生成总结

**功能流程：**
```
转写文字
    ↓
星火大模型生成结构化总结

课程总结包含：
  - 主题
  - 核心知识点
  - 重点难点
  - 金句
  - 预习建议

会议总结包含：
  - 主题
  - 讨论要点
  - 决议事项
  - 待办事项
```

#### 2.4.3 导出功能

**支持格式：**
- DOCX（python-docx）：结构化总结文档
- PPTX（python-pptx）：课程PPT演示文稿

### 2.5 AI学姐对话

#### 2.5.1 校园专属问答

**技术实现：**
- ChromaDB RAG知识库检索
- 讯飞星火大模型生成回答
- 联动课程、日程、回顾记录等数据

#### 2.5.2 语音交互

**语音输入：**
- 讯飞ASR：语音输入 → 识别为文字
- 支持实时语音识别（WebSocket）

**语音播报：**
- 讯飞TTS：回复文字 → 合成语音播放

#### 2.5.3 情感陪伴模式

**功能说明：**
- 点击❤️切换为温暖倾听模式
- 讯飞NLP情感分析识别负面情绪
- 自动调整回复语气和内容

### 2.6 智能翻译

#### 2.6.1 即时翻译

**功能说明：**
- 用户在左侧输入文本
- 选择目标语言
- 点击翻译按钮后右侧实时输出翻译结果

**支持语言：**
| 语言 | 代码 |
|-----|------|
| 中文 | zh |
| 英文 | en |
| 日文 | ja |
| 韩文 | ko |
| 法文 | fr |
| 德文 | de |
| 西班牙文 | es |
| 俄文 | ru |
| 阿拉伯文 | ar |

**技术实现：**
- 使用讯飞星火大模型的文本翻译能力
- 支持多语言互译
- 翻译结果可一键复制

#### 2.6.2 文档翻译

**支持格式：**
- .txt 文件：直接读取文本内容
- .docx 文件：使用 python-docx 库解析段落

**功能流程：**
```
用户上传文档(txt/docx)
    ↓
选择目标语言
    ↓
点击翻译
    ↓
后端解析文档内容 → 分段落调用星火翻译API
    ↓
返回翻译结果 → 前端展示预览
    ↓
用户可导出为Word文档
```

### 2.7 智能选课助手

#### 2.7.1 功能说明

根据学生专业和规划，通过AI推荐选课方案。

#### 2.7.2 技术实现

**输入：**
- 学生专业
- 学习规划
- 兴趣爱好

**输出：**
- 推荐课程列表
- 课程简介
- 选择理由

### 2.8 校园活动助手

#### 2.8.1 活动策划生成

**输入表单：**
| 字段 | 类型 | 说明 |
|-----|------|------|
| 活动类型 | 下拉选择 | 文艺类、体育类、学术类、志愿类、团建类、其他 |
| 活动主题 | 文本输入 | 例如"校园歌手大赛" |
| 预计人数 | 下拉选择 | 小规模(≤50)、中规模(50-200)、大规模(≥200) |
| 预算范围 | 下拉选择 | 低(<500元)、中(500-2000元)、高(>2000元) |
| 活动时间 | 日期选择 | 初步意向日期 |
| 特殊需求 | 多选框 | 需要抽奖、需要嘉宾、室外活动、线上活动 |

**AI输出：**
- 活动名称
- 活动概述
- 时间安排
- 人员分工
- 预算清单
- 风险预案
- 宣传方案

#### 2.8.2 宣传文案生成

**生成的文案类型：**
| 文案类型 | 用途 | 字数 |
|---------|------|-----|
| 海报主标题 | 制作海报用 | 5-15字 |
| 朋友圈短文案 | 朋友圈/QQ空间 | 50-100字 |
| 公众号推文 | 公众号/抖音描述 | 300-500字 |
| 邀请函 | 正式邀请嘉宾/领导 | 200-300字 |
| 广播稿 | 学校广播站 | 100-200字 |

#### 2.8.3 飞书群推送

**预配置群列表：**
| 群标识 | 显示名称 | 用途 |
|-------|---------|------|
| student_union | 学生会通知 | 学生会活动通知 |
| club_alliance | 社团联盟 | 社团联合活动 |
| class_group | 班级通知 | 班级团日活动 |
| youth_union | 团委通知 | 团委活动通知 |
| dormitory | 宿舍管理 | 宿舍活动 |

---

## 三、教师端功能

### 3.1 功能总览

| 功能 | 说明 | 优先级 | 状态 |
|-----|-----|-------|-----|
| 教师登录注册 | 手机号注册/登录，角色认证 | P0 | ✅ 已完成 |
| 智能成绩管理 | 上传Excel、AI自动计算、生成图表 | P0 | ✅ 已完成 |
| 智能通知发布 | 输入关键词，AI生成格式规范通知 | P0 | ✅ 已完成 |
| 智能备课教案生成 | 输入知识点，AI生成教学大纲和PPT | P1 | 🔄 开发中 |

### 3.2 登录注册

#### 3.2.1 功能流程

```
手机号注册 → 验证身份（教师）→ 进入教师端
```

#### 3.2.2 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| phone | string | 手机号 |
| password | string | 密码 |
| name | string | 教师姓名 |
| department | string | 院系 |
| course | string | 教授课程 |

#### 3.2.3 权限控制

- 教师角色（role=teacher）只能访问教师端
- 学生角色（role=student）只能访问学生端

#### 3.2.4 页面路径

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 登录页 | /teacher/login | 教师手机号登录 |
| 注册页 | /teacher/register | 教师注册 |
| 首页 | /teacher | 教师端首页（功能入口） |

### 3.3 智能成绩管理

#### 3.3.1 功能概述

教师上传Excel成绩表，系统自动解析、AI计算、生成可视化图表，支持导出。

#### 3.3.2 成绩表上传

**成绩表格式要求：**
| 列名 | 说明 | 必填 |
|-----|------|-----|
| 学生姓名 | 文本 | 是 |
| 学号 | 文本 | 否 |
| 平时分 | 数字 | 是 |
| 期中分 | 数字 | 否 |
| 期末分 | 数字 | 是 |
| 实验/实践分 | 数字 | 否 |

**技术实现：**
- 使用 openpyxl 解析 Excel 文件
- 自动查找表头行（处理标题行情况）
- 支持多种表头格式

#### 3.3.3 AI自动计算

**计算规则：**
- 总评 = 平时分 × 权重1 + 期中分 × 权重2 + 期末分 × 权重3 + 实验分 × 权重4
- 权重默认：平时40% 期中20% 期末40%
- 缺考/缓考标记为"缓考"/"缺考"，不参与计算
- 按总评降序计算排名

**权重配置：**
| 成绩项 | 默认权重 | 可配置范围 |
|-------|---------|-----------|
| 平时分 | 40% | 0-100% |
| 期中分 | 20% | 0-100% |
| 期末分 | 40% | 0-100% |
| 实验分 | 0% | 0-100% |

#### 3.3.4 可视化图表

**图表类型：**
| 图表 | 说明 | 技术实现 |
|-----|------|---------|
| 成绩分布直方图 | 按区间：<60, 60-70, 70-80, 80-90, >90 | ECharts 柱状图 |
| 学生能力雷达图 | 单个学生各项能力对比 | ECharts 雷达图 |
| 各单项成绩统计 | 平时、期中、期末、实验各项均分 | ECharts 折线图 |

#### 3.3.5 AI分析报告

**使用讯飞星火大模型生成分析报告，包含：**
- 班级概述（平均分、及格率、最高分、最低分）
- 高分学生名单
- 需关注学生
- 试卷分析（难度、区分度）
- 教学建议

#### 3.3.6 导出功能

| 导出类型 | 格式 | 说明 |
|---------|------|-----|
| 成绩表 | .xlsx | 完整成绩数据 |
| 统计图表 | .png | ECharts图表截图 |

#### 3.3.7 页面路径

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 成绩管理主页 | /teacher/grade | 成绩表上传+AI分析 |
| 成绩详情页 | /teacher/grade/:id | 成绩图表展示 |

### 3.4 智能通知发布

#### 3.4.1 功能概述

教师输入通知主题和补充信息，AI自动生成格式规范的通知文档，支持一键发送到飞书群。

#### 3.4.2 通知类型

| 类型 | 标识 | 说明 |
|-----|------|------|
| 考试通知 | exam | 期末/期中考试安排 |
| 会议通知 | meeting | 教师/班级会议 |
| 活动通知 | activity | 校园活动 |
| 放假通知 | holiday | 节假日放假安排 |
| 征稿通知 | submission | 征文/投稿征集 |
| 其他通知 | other | 其他类型 |

#### 3.4.3 输入字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| 通知类型 | 下拉选择 | 是 | 如上表 |
| 通知主题 | 文本输入 | 是 | 例如"关于期末考试安排的通知" |
| 补充信息 | 文本输入 | 否 | 考试时间、地点、会议议程等 |

#### 3.4.4 输出内容

AI生成的通知包含：
- **标题**：`【通知】+ 主题`
- **称呼**：尊敬的各位同学/老师
- **正文**：分点列出，逻辑清晰
- **落款**：广州商学院XX学院 + 日期

#### 3.4.5 发送功能

- **复制通知**：一键复制到剪贴板
- **飞书推送**：选择预配置的飞书群组发送

#### 3.4.6 页面路径

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 通知发布页 | /teacher/notification | AI生成通知 |

### 3.5 智能备课教案生成

#### 3.5.1 功能概述

帮助教师快速生成教学大纲和PPT演示文稿，基于讯飞智能PPT生成API。

#### 3.5.2 用户交互流程

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  教师输入   │ ──▶ │  AI生成大纲   │ ──▶ │  教师确认   │ ──▶ │  生成PPT    │
│  课程信息   │     │  （可调整）   │     │  大纲       │     │  下载        │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

**两种模式：**
1. **快速模式**：直接输入要求，AI一次性生成大纲+PPT
2. **分步模式**：先生成大纲 → 教师确认/修改 → 再生成PPT

#### 3.5.3 输入字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| 教案标题 | 文本输入 | 是 | 教案名称 |
| 课程名称 | 文本输入 | 否 | 例如"市场营销" |
| 知识点描述 | 文本输入 | 是 | 至少10字 |
| 授课对象 | 文本输入 | 否 | 例如"大二学生" |
| 课时数 | 数字 | 否 | 默认2学时 |
| PPT模板ID | 选择 | 否 | 选择PPT主题模板 |

#### 3.5.4 讯飞PPT API

**API接口：**
| 接口 | 方法 | 地址 | 用途 |
|-----|------|------|------|
| 主题列表查询 | POST | `/v2/aippt/theme/list` | 获取可选PPT模板 |
| PPT直接生成 | POST | `/v2/aippt/create` | 输入要求，直接生成PPT |
| 大纲生成 | POST | `/v2/aippt/createOutline` | 只生成大纲，不生成PPT |
| 通过大纲生成PPT | POST | `/v2/aippt/createPPTByOutline` | 基于已有大纲生成PPT |
| PPT进度查询 | POST | `/v2/aippt/process` | 查询PPT生成状态 |

#### 3.5.5 页面路径

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 备课教案页 | /teacher/lesson-plan | AI生成教案+PPT |

---

## 四、讯飞API能力矩阵

### 4.1 API能力总览

| 能力域 | API | 集成功能 | 调用方式 |
|-------|-----|---------|---------|
| 星火大模型 | Spark API | AI对话、总结生成、选课建议、意图解析、翻译、通知生成、教案生成 | REST/WebSocket |
| 语音识别 | ASR | 语音输入、录音转写 | REST API |
| 语音合成 | TTS | AI回复播报、情感模式 | REST API |
| 文字识别 | OCR | 课表图片识别 | REST API |
| NLP分析 | NLP SA | 情感分析 | REST API |
| 智能PPT | AIPPT | 教案PPT生成 | REST API |

### 4.2 学生端API调用

| 功能 | 使用API | 调用时机 | 重试 |
|-----|--------|---------|-----|
| 语音输入 | ASR | 用户按住麦克风 | ✅ |
| 录音转写 | ASR(file) | 用户上传MP3 | ✅ |
| 语音播报 | TTS | 用户点击播放 | ✅ |
| 课表识别 | OCR | 用户上传课表图片 | ✅ |
| AI对话 | 星火chat | 用户发送消息 | ✅ |
| 课程总结 | 星火chat | 转写完成后 | ✅ |
| 情感分析 | NLP SA | 用户发送消息时 | ✅ |
| 意图解析 | 星火chat | 用户添加日程时 | ✅ |
| 即时翻译 | 星火chat | 用户点击翻译 | ✅ |
| 文档翻译 | 星火chat | 用户上传文档 | ✅ |
| 活动策划 | 星火chat | 用户生成策划 | ✅ |
| 宣传文案 | 星火chat | 用户生成文案 | ✅ |

### 4.3 教师端API调用

| 功能 | 使用API | 调用时机 | 重试 |
|-----|--------|---------|-----|
| 成绩分析报告 | 星火chat | 上传成绩后 | ✅ |
| 通知生成 | 星火chat | 用户点击生成 | ✅ |
| 大纲生成 | 星火chat | 用户点击生成 | ✅ |
| PPT生成 | 讯飞AIPPT | 用户点击生成 | ✅ |

### 4.4 鉴权机制

讯飞API使用 HMAC-SHA256 签名鉴权：

```python
# 1. 构建待签名字符串
signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"

# 2. HMAC-SHA256签名
signature_sha = hmac.new(
    api_secret.encode('utf-8'),
    signature_origin.encode('utf-8'),
    digestmod=hashlib.sha256
).digest()

# 3. Base64编码
authorization = base64.b64encode(signature_sha).decode('utf-8')
```

### 4.5 重试机制

所有讯飞API调用必须实现3次重试，间隔递增：

```python
for attempt in range(3):
    try:
        result = await call_xfyun_api()
        return result
    except Exception as e:
        if attempt < 2:
            await asyncio.sleep(1.0 * (attempt + 1))
        else:
            raise ThirdPartyException("Service name", str(e))
```

---

## 五、数据库设计

### 5.1 核心数据表

#### 5.1.1 用户表（users）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| phone | VARCHAR(20) | 手机号 |
| password | VARCHAR(255) | 密码（哈希） |
| nickname | VARCHAR(100) | 昵称 |
| role | ENUM('student', 'teacher') | 角色 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.2 学生画像表（student_profiles）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 外键关联users |
| major | VARCHAR(100) | 专业 |
| grade | VARCHAR(20) | 年级 |
| goal | TEXT | 学习目标 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.3 教师画像表（teacher_profiles）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 外键关联users |
| department | VARCHAR(100) | 院系 |
| office | VARCHAR(100) | 办公室 |
| title | VARCHAR(50) | 职称 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.4 课程表（courses）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 外键关联users |
| name | VARCHAR(100) | 课程名 |
| teacher | VARCHAR(100) | 任课教师 |
| location | VARCHAR(100) | 上课地点 |
| day_of_week | INT | 星期几（1-7） |
| start_slot | INT | 开始节次 |
| end_slot | INT | 结束节次 |
| start_time | TIME | 开始时间 |
| end_time | TIME | 结束时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.5 日程表（schedules）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 外键关联users |
| title | VARCHAR(200) | 日程标题 |
| content | TEXT | 日程内容 |
| location | VARCHAR(100) | 地点 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| is_all_day | TINYINT | 是否全天 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.6 录音回顾表（reviews）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| user_id | INT | 外键关联users |
| title | VARCHAR(200) | 回顾标题 |
| type | ENUM('course', 'meeting') | 类型 |
| audio_url | VARCHAR(500) | 音频URL |
| transcript | TEXT | 转写文字 |
| summary | TEXT | AI总结 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.7 成绩记录表（grade_records）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| teacher_id | INT | 外键关联users |
| course_name | VARCHAR(255) | 课程名称 |
| semester | VARCHAR(50) | 学期 |
| class_name | VARCHAR(100) | 班级名称 |
| weights | JSON | 权重配置 |
| ai_report | TEXT | AI分析报告缓存 |
| stats_data | JSON | 统计数据 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_deleted | TINYINT | 软删除标记 |

#### 5.1.8 成绩明细表（grade_items）

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| record_id | INT | 外键关联grade_records |
| student_name | VARCHAR(100) | 学生姓名 |
| student_no | VARCHAR(50) | 学号 |
| usual_score | DECIMAL(5,2) | 平时分 |
| midterm_score | DECIMAL(5,2) | 期中分 |
| final_score | DECIMAL(5,2) | 期末分 |
| practice_score | DECIMAL(5,2) | 实验分 |
| total_score | DECIMAL(5,2) | 总评 |
| ranking | INT | 排名 |
| status | ENUM('normal', 'absent', 'deferred') | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

---

## 六、API接口规范

### 6.1 统一响应格式

**成功响应：**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  }
}
```

### 6.2 学生端API

#### 认证相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 获取当前用户信息 |

#### 课表相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| GET | /api/timetable | 获取课表 |
| POST | /api/timetable/import | OCR导入课表 |
| GET | /api/timetable/today | 获取今日课程 |

#### 日程相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| GET | /api/schedule | 获取日程列表 |
| POST | /api/schedule | 创建日程 |
| DELETE | /api/schedule/{id} | 删除日程 |

#### 录音回顾相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| GET | /api/review | 获取回顾列表 |
| POST | /api/review | 创建回顾（上传录音） |
| GET | /api/review/{id} | 获取回顾详情 |
| DELETE | /api/review/{id} | 删除回顾 |

#### AI对话相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/chat | 发送消息 |
| WebSocket | /api/chat/ws | WebSocket实时对话 |

#### 翻译相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/translate/text | 即时翻译 |
| POST | /api/translate/document | 文档翻译 |

#### 选课相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/course-advisor/recommend | 获取选课推荐 |

#### 活动相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/activity/generate-plan | 生成活动策划 |
| POST | /api/activity/generate-copy | 生成宣传文案 |
| POST | /api/activity/send-feishu | 发送到飞书 |

### 6.3 教师端API

#### 认证相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/auth/teacher/register | 教师注册 |
| POST | /api/auth/teacher/login | 教师登录 |

#### 成绩相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/teacher/grade/upload | 上传成绩Excel |
| GET | /api/teacher/grade/records | 获取成绩记录列表 |
| GET | /api/teacher/grade/records/{id} | 获取成绩详情 |
| GET | /api/teacher/grade/records/{id}/report | 获取AI分析报告 |
| DELETE | /api/teacher/grade/records/{id} | 删除成绩记录 |
| GET | /api/teacher/grade/records/{id}/export | 导出成绩Excel |

#### 通知相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/teacher/notification/generate | AI生成通知 |
| GET | /api/teacher/notification/groups | 获取飞书群组列表 |
| POST | /api/teacher/notification/send | 发送到飞书群 |

#### 教案相关

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | /api/teacher/lesson-plan/ | 创建教案 |
| GET | /api/teacher/lesson-plan/themes | 获取PPT模板列表 |
| POST | /api/teacher/lesson-plan/generate-outline | 生成教学大纲 |
| POST | /api/teacher/lesson-plan/generate-ppt | 生成PPT |
| GET | /api/teacher/lesson-plan/ppt-status/{sid} | 查询PPT生成状态 |

---

## 七、页面结构

### 7.1 学生端页面

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 登录页 | /login | 手机号登录 |
| 引导页 | /guide | 首次登录完善信息 |
| 首页 | / | 今日课程+日程+快捷入口 |
| 课表管理 | /timetable | 课程列表 |
| 课表导入 | /timetable/import | OCR导入 |
| 日程管理 | /schedule | 日程列表 |
| 录音回顾 | /review | 回顾记录列表 |
| 回顾详情 | /review/:id | 总结展示+导出 |
| 智能翻译 | /translate | 即时翻译+文档翻译 |
| 选课助手 | /course-advisor | 选课咨询 |
| 校园活动助手 | /activity | 活动策划+文案生成+飞书推送 |
| AI学姐 | /ai-sister | 核心对话页面 |
| 个人中心 | /profile | 用户信息 |

### 7.2 教师端页面

| 页面 | 路径 | 说明 |
|-----|-----|-----|
| 登录页 | /teacher/login | 教师手机号登录 |
| 注册页 | /teacher/register | 教师注册 |
| 首页 | /teacher | 教师端首页（功能入口） |
| 成绩管理 | /teacher/grade | 成绩表上传+AI分析 |
| 成绩详情 | /teacher/grade/:id | 成绩图表展示 |
| 通知发布 | /teacher/notification | AI生成通知 |
| 备课教案 | /teacher/lesson-plan | AI生成教案+PPT |
| 个人中心 | /teacher/profile | 教师信息 |

---

## 八、非功能需求

### 8.1 性能指标

| 指标 | 要求 |
|-----|-----|
| 页面加载 | ≤2秒 |
| API响应 | ≤3秒（不含AI推理） |
| ASR转写 | 1分钟音频≤30秒 |
| 并发 | 支持≥50人同时在线 |
| 浏览器 | Chrome/Safari/Edge/Firefox最新版 |

### 8.2 约束条件

| 类型 | 限制 |
|-----|------|
| 成绩Excel文件大小 | ≤5MB |
| 单次生成PPT页数 | ≤50页 |
| 录音文件大小 | ≤50MB |
| 文档翻译文件 | ≤5MB |

---

## 九、技术亮点与经验

### 9.1 技术亮点

1. **讯飞API全能力集成**：ASR、TTS、OCR、星火大模型、NLP语义分析、PPT生成
2. **RAG知识库**：ChromaDB向量数据库实现智能问答
3. **异步架构**：FastAPI + SQLAlchemy异步ORM + aiomysql
4. **双端适配**：Element Plus(PC) + Vant(移动端)
5. **统一错误处理**：规范化错误码和日志记录
6. **重试机制**：所有外部API调用实现3次重试

### 9.2 开发经验

1. **讯飞API规范**：不同产品使用不同域名和签名算法，需仔细阅读文档
2. **Excel解析**：注意处理标题行、合并单元格等复杂情况
3. **前端状态管理**：统一使用Pinia，分层管理Page/Store/API
4. **数据库迁移**：使用ORM的create_all或alembic管理表结构
5. **日志规范**：统一日志格式，便于问题追踪

---

## 十、测试账号

### 10.1 学生账号

| 账号 | 密码 | 说明 |
|-----|------|-----|
| 13356405812 | 123456 | 测试学生账号 |

### 10.2 教师账号

| 账号 | 密码 | 说明 |
|-----|------|-----|
| 13356405811 | 123456 | 测试教师账号 |

---

## 附录

### A. 讯飞API域名

| 产品 | 域名 |
|-----|------|
| 星火大模型 | spark-api-open.xf-yun.com |
| 智能PPT | zwapi.xfyun.cn |
| 语音识别 | api.xf-yun.com |
| 语音合成 | api.xf-yun.com |
| OCR | api.xf-yun.com |
| NLP | api.xf-yun.com |

### B. 环境变量

```bash
# 数据库
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/ai_xiaoshang

# 讯飞开放平台
XFYUN_APP_ID=your_app_id
XFYUN_API_KEY=your_api_key
XFYUN_API_SECRET=your_api_secret

# JWT认证
SECRET_KEY=change-this-to-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 文件上传
UPLOAD_DIR=uploads
MAX_AUDIO_SIZE_MB=50
MAX_IMAGE_SIZE_MB=5
```

---

**文档版本：** 1.0
**最后更新：** 2026年5月8日
**维护者：** AI小商开发团队
