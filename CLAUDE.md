# AI小商 - Claude Code 开发规范

> 本文件是 AI小商 项目的开发指南，定义代码规范、错误处理、日志记录、项目结构等核心规则。
> 所有开发工作必须遵循本文件的规范。

---

## 项目概览

| 项目名称 | AI小商 |
|---------|--------|
| 项目定位 | 面向广州商学院师生的智慧校园AI助手（比赛演示用） |
| 技术栈 | Vue.js 3 + FastAPI + MySQL + ChromaDB + 讯飞开放平台 |
| 代码仓库 | `/Users/salmon/Desktop/Xunfei project/AI小商/` |
| 文档目录 | `docs/` |

---

## 目录结构规范

```
AI小商/
├── frontend/                    # Vue.js 前端项目
│   ├── src/
│   │   ├── api/               # API 接口封装（按模块划分）
│   │   ├── assets/            # 静态资源
│   │   ├── components/        # 公共组件（按功能域划分）
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理（按模块划分）
│   │   ├── utils/             # 工具函数
│   │   └── views/             # 页面视图（按模块划分）
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # FastAPI 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # 应用入口
│   │   ├── config.py         # 配置管理（必须从此处导入配置）
│   │   ├── database.py       # 数据库连接
│   │   ├── models/           # SQLAlchemy 模型（按模块划分）
│   │   ├── schemas/          # Pydantic 模型（按模块划分）
│   │   ├── routers/          # API 路由（按模块划分）
│   │   ├── services/         # 业务逻辑层（按能力划分）
│   │   └── utils/            # 工具函数
│   ├── scripts/              # 数据库初始化脚本
│   └── requirements.txt
│
├── docs/                      # 项目文档（统一入口：README.md）
│   ├── README.md             # 文档总览（必读）
│   ├── 项目规范.md            # 本文件
│   ├── 产品需求PRD.md         # 产品需求文档
│   ├── 技术方案.md            # 系统架构与技术实现
│   ├── 数据库设计.md          # 数据库详细设计
│   ├── 接口规范.md            # API 接口规范
│   ├── 前端开发指南.md        # 前端开发规范与组件说明
│   ├── 后端开发指南.md        # 后端开发规范与服务说明
│   └── 部署运维.md            # 部署与运维指南
│
├── nginx/                     # Nginx 配置
├── docker-compose.yml         # Docker 编排（不含Redis）
├── .env.example              # 环境变量示例
└── README.md                  # 项目根目录说明
```

---

## UI/UX 设计规范

### 1. 设计风格定位

**主题风格：清新校园风（Fresh Campus UI）**

融合浅色清爽背景、青色主色调、简洁现代卡片设计，打造清新、专业、有温度的智慧校园AI助手界面。风格特点：清新、专业、现代、易用。

### 2. 色彩系统

#### 2.1 主色调

| 角色 | 色值 | 用途 |
|-----|------|------|
| **主色-青色** | `#0891B2` | 核心交互元素、按钮、链接 |
| **主色-亮青** | `#22D3EE` | 悬停状态、渐变 |
| **主色-深青** | `#0E7490` | 按下状态 |
| **辅助色-薄荷绿** | `#059669` | 成功状态、辅助信息 |
| **辅助色-天蓝** | `#0284C7` | 信息提示 |
| **强调色-紫色** | `#8B5CF6` | 特色功能标签 |
| **警告色-红色** | `#EF4444` | 警告、删除、紧急操作 |

#### 2.2 背景色

| 层级 | 色值 | 用途 |
|-----|------|------|
| **页面背景** | `#F8FAFC` | 页面主背景（浅灰） |
| **卡片背景** | `#FFFFFF` | 卡片、面板背景 |
| **悬浮层** | `#F1F5F9` | 按钮悬停、下拉菜单 |
| **边框色** | `#E2E8F0` | 卡片边框、分隔线 |

#### 2.3 文字色

| 层级 | 色值 | 用途 |
|-----|------|------|
| **主文字** | `#1E293B` | 标题、重要文字 |
| **正文文字** | `#475569` | 正文内容 |
| **次要文字** | `#94A3B8` | 辅助说明 |
| **禁用文字** | `#CBD5E1` | 时间戳、次要信息 |

#### 2.4 边框与分割线

| 类型 | 色值 | 用途 |
|-----|------|------|
| **默认边框** | `#E2E8F0` | 卡片、输入框边框 |
| **悬停边框** | `#CBD5E1` | 悬停状态 |
| **激活边框** | `#0891B2` | 选中状态 |
| **分割线** | `#F1F5F9` | 列表分割 |

### 3. 字体系统

#### 3.1 字体选择

| 用途 | 字体 | 备选 |
|-----|------|------|
| **中文字体** | `Noto Sans SC` | `PingFang SC`, `Microsoft YaHei` |
| **英文字体** | `Inter` | `system-ui` |
| **等宽字体** | `JetBrains Mono` | `Fira Code`, `Source Code Pro` |

#### 3.2 字号规范

| 层级 | PC端 | 移动端 | 用途 |
|-----|------|-------|------|
| `text-hero` | 48px | 32px | 落地页大标题 |
| `text-h1` | 36px | 28px | 页面主标题 |
| `text-h2` | 28px | 22px | 区块标题 |
| `text-h3` | 22px | 18px | 卡片标题 |
| `text-body` | 16px | 15px | 正文内容 |
| `text-small` | 14px | 13px | 辅助说明 |
| `text-xs` | 12px | 12px | 标签、时间戳 |

#### 3.3 行高与字重

- 标题行高：`1.2`（紧凑）
- 正文行高：`1.6`（舒适）
- 正文字重：`400`
- 标题字重：`600-700`

### 4. 卡片设计

#### 4.1 清新卡片

```css
.fresh-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.2s ease;
}

.fresh-card:hover {
  border-color: #CBD5E1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}
```

#### 4.2 渐变按钮

```css
.btn-primary {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  color: #FFFFFF;
  font-weight: 600;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}
```

#### 4.3 输入框

```css
.fresh-input {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  color: #1E293B;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.fresh-input:focus {
  outline: none;
  border-color: #0891B2;
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
}

.fresh-input::placeholder {
  color: #CBD5E1;
}
```

### 5. 阴影效果

#### 5.1 主色阴影

```css
.shadow-primary {
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.shadow-success {
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
}

.shadow-danger {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}
```

#### 5.2 文字渐变效果

```css
.text-gradient {
  background: linear-gradient(135deg, #0891B2, #34D399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

#### 5.3 卡片悬浮效果

```css
.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}
```

### 6. 背景与加载

#### 6.1 简洁背景

```css
.page-background {
  background: #F8FAFC;
}

.card-background {
  background: #FFFFFF;
}
```

#### 6.2 加载动画

```css
.loading-spinner {
  border: 2px solid rgba(8, 145, 178, 0.2);
  border-top-color: #0891B2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```
```

### 7. 动画规范

#### 7.1 过渡时长

| 动画类型 | 时长 | 缓动函数 |
|---------|------|---------|
| 微交互 | `150ms` | `ease-out` |
| 常规过渡 | `300ms` | `ease-in-out` |
| 复杂动画 | `500ms` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| 页面切换 | `300ms` | `ease-in-out` |

#### 7.2 悬停效果

```css
/* 卡片悬停 */
.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: #CBD5E1;
}

/* 按钮悬停 */
.btn-primary {
  position: relative;
  overflow: hidden;
}

.btn-primary::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.btn-primary:hover::after {
  transform: translateX(100%);
}
```

#### 7.3 加载动画

```css
/* 脉冲加载 */
.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 旋转加载 */
.loading-spinner {
  border: 2px solid rgba(8, 145, 178, 0.2);
  border-top-color: #0891B2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### 8. 组件设计规范

#### 8.1 导航栏

```css
.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #E2E8F0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 0 24px;
  height: 64px;
}
```

#### 8.2 卡片组件

```css
.card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}
```

#### 8.3 标签/徽章

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 20px;
  font-size: 12px;
  color: #0891B2;
}
```

### 9. 前端页面规范

#### 9.1 页面布局

- 使用 `max-width: 1200px` 限制内容最大宽度
- 页面内容添加 `padding: 24px` 内边距
- 底部内容添加 `padding-bottom: 100px` 避免被固定导航栏遮挡
- 移动端响应式断点：`768px`（平板）、`1024px`（桌面）

#### 9.2 浅色主题适配

所有颜色使用 CSS 变量：

```css
/* 正确写法 */
.bg-page { background-color: #F8FAFC; }
.bg-card { background-color: #FFFFFF; }
.text-primary { color: #1E293B; }

/* Element Plus 浅色主题覆盖 */
.el-button--primary {
  --el-button-bg-color: #0891B2;
  --el-button-border-color: #0891B2;
  --el-button-hover-bg-color: #22D3EE;
  --el-button-hover-border-color: #22D3EE;
}
```

### 10. 视觉检查清单

- [ ] 无 emoji 作为图标（统一使用 SVG 图标如 Heroicons/Lucide）
- [ ] 悬停状态不导致页面跳动
- [ ] 所有可点击元素有 `cursor-pointer`
- [ ] 阴影效果温和不刺眼
- [ ] 浅色模式文字对比度 ≥ 4.5:1
- [ ] 卡片效果在浅色背景上清晰可见
- [ ] 动画流畅（60fps）
- [ ] 移动端无水平滚动

---

## 开发计划

### 1. 项目里程碑

| 阶段 | 日期 | 目标 |
|-----|------|------|
| M1 | Day 1 | 项目初始化 + 基础框架搭建完成 |
| M2 | Day 2-3 | 核心功能开发（讯飞API集成） |
| M3 | Day 4-5 | 功能完善 + 前端界面开发 |
| M4 | Day 6 | 系统集成 + 文档完善 |
| M5 | Day 7 | 演示准备 + 最终调试 |

### 2. 每日任务分配

#### Day 1：项目初始化

**前端负责人**
- [ ] 初始化 Vue 3 + Vite 项目
- [ ] 配置 Tailwind CSS + 深色主题
- [ ] 安装 Element Plus + Vant
- [ ] 配置路由和 Pinia Store
- [ ] 搭建项目框架结构

**后端负责人**
- [ ] 初始化 FastAPI 项目
- [ ] 配置 MySQL 数据库连接
- [ ] 实现讯飞API鉴权模块
- [ ] 创建数据库模型
- [ ] 编写基础 API 路由骨架

**内容/测试**
- [ ] 完善讯飞开放平台账号配置
- [ ] 准备测试用图片/音频素材
- [ ] 编写 RAG 知识库内容

#### Day 2：讯飞API集成

**前端负责人**
- [ ] 开发登录注册页面
- [ ] 封装讯飞 WebSocket 组件
- [ ] 开发语音录制组件

**后端负责人**
- [ ] 实现星火大模型对话API
- [ ] 实现 ASR 语音识别API
- [ ] 实现 TTS 语音合成API
- [ ] 实现 OCR 文字识别API
- [ ] 实现 NLP 情感分析API
- [ ] 配置 ChromaDB RAG 知识库

**内容/测试**
- [ ] 测试各讯飞API功能
- [ ] 准备对话知识库内容

#### Day 3：核心功能开发

**前端负责人**
- [ ] 开发课表管理页面（导入/展示）
- [ ] 开发 AI 对话界面
- [ ] 开发录音回顾页面上传

**后端负责人**
- [ ] 实现课表OCR解析逻辑
- [ ] 实现 AI 学姐对话逻辑
- [ ] 实现录音转写 + 总结生成
- [ ] 实现 DOCX/PPTX 导出

#### Day 4：功能完善

**前端负责人**
- [ ] 开发选课助手页面
- [ ] 开发校园活动助手页面
- [ ] 开发管理后台界面
- [ ] 优化动画和视觉效果

**后端负责人**
- [ ] 实现选课推荐逻辑
- [ ] 实现活动助手逻辑
- [ ] 开发管理后台API
- [ ] 添加数据统计接口

#### Day 5：界面美化与集成

**前端负责人**
- [ ] 应用赛博朋克设计风格
- [ ] 添加粒子/网格背景效果
- [ ] 优化玻璃拟态效果
- [ ] 添加霓虹发光动画
- [ ] 完善响应式布局

**后端负责人**
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 日志记录优化
- [ ] API 文档完善

#### Day 6：系统集成

**全员**
- [ ] Docker 部署配置
- [ ] 前后端联调
- [ ] 功能测试与修复
- [ ] 文档审核与完善

#### Day 7：演示准备

**全员**
- [ ] 演示流程演练
- [ ] 演示数据准备
- [ ] 截图/录屏素材准备
- [ ] 最终bug修复
- [ ] 提交物打包

### 3. 技术债务清理

以下内容在开发过程中需注意避免，后续统一处理：

| 类型 | 说明 | 处理时机 |
|-----|------|---------|
| 硬编码 | 禁止在代码中硬编码配置 | 开发时 |
| Console.log | 前端代码中的调试日志需删除 | 提交前 |
| 重复代码 | 相似功能需抽离为公共组件/函数 | 开发时 |
| 未使用变量 | 及时清理未使用的导入和变量 | 提交前 |
| Magic Numbers | 使用常量替代魔法数字 | 开发时 |

### 4. 演示检查清单

#### 功能演示
- [ ] 登录注册流程正常
- [ ] 课表OCR导入成功
- [ ] AI对话响应正常
- [ ] 语音识别工作正常
- [ ] 录音转写+总结正常
- [ ] DOCX导出正常
- [ ] PPTX导出正常
- [ ] 选课助手展示正常
- [ ] 管理后台可访问

#### 视觉效果
- [ ] 深色主题正确显示
- [ ] 玻璃拟态效果可见
- [ ] 霓虹发光效果正常
- [ ] 动画流畅无卡顿
- [ ] 页面响应式正常

#### 演示准备
- [ ] 讯飞API额度充足
- [ ] 网络连接稳定
- [ ] 备用设备已准备
- [ ] 演示时间控制在5分钟内

---

## 错误处理规范

### 1. 后端错误处理

#### 1.1 统一错误响应格式

```python
# backend/app/utils/errors.py

from fastapi import HTTPException, status
from typing import Optional, Any
import traceback
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    """应用级异常基类"""
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self):
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }

class NotFoundException(AppException):
    """资源不存在"""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            status_code=404
        )

class ValidationException(AppException):
    """数据验证失败"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )

class ThirdPartyException(AppException):
    """第三方服务异常（如讯飞API）"""
    def __init__(self, service: str, message: str, original_error: Exception = None):
        logger.error(f"[{service}] Third party error: {message}", exc_info=original_error)
        super().__init__(
            message=f"{service} error: {message}",
            code="THIRD_PARTY_ERROR",
            status_code=502,
            details={"service": service, "original_error": str(original_error)}
        )

# 异常处理装饰器
from functools import wraps

def handle_app_errors(func):
    """统一异常处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppException as e:
            raise e
        except Exception as e:
            logger.error(f"[{func.__name__}] Unexpected error: {str(e)}", exc_info=True)
            raise AppException(
                message="Internal server error",
                code="INTERNAL_ERROR",
                status_code=500,
                details=str(e) if __debug__ else None
            )
    return wrapper
```

#### 1.2 在 router 中的标准用法

```python
# backend/app/routers/example.py

from fastapi import APIRouter, Depends, HTTPException
from app.utils.errors import (
    NotFoundException,
    ValidationException,
    ThirdPartyException,
    handle_app_errors
)

router = APIRouter(prefix="/api/example", tags=["示例"])

@router.get("/{item_id}")
@handle_app_errors
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise NotFoundException("Item", item_id)
    return {"id": item.id, "name": item.name}

@router.post("/")
@handle_app_errors
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    if not item.name:
        raise ValidationException("name is required", {"field": "name"})
    # ...
```

#### 1.3 讯飞API错误处理

```python
# backend/app/services/xinghuo_service.py

import logging
logger = logging.getLogger(__name__)

class XingHuoService:
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # 秒

    async def chat_with_retry(self, messages: List[Dict]) -> str:
        """带重试的星火大模型调用"""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self._do_chat(messages)
                logger.info(f"[XingHuo] Chat success, tokens used: {len(messages)}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[XingHuo] Chat failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    import asyncio
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))

        # 所有重试都失败
        from app.utils.errors import ThirdPartyException
        raise ThirdPartyException(
            service="XingHuo",
            message="星火大模型调用失败，请稍后重试",
            original_error=last_error
        )
```

### 2. 前端错误处理

#### 2.1 统一错误处理

```javascript
// frontend/src/utils/errorHandler.js

import { ElMessage } from 'element-plus'

/**
 * 统一错误处理函数
 * @param {Error} error - 错误对象
 * @param {Object} options - 配置选项
 */
export function handleError(error, options = {}) {
  const { showMessage = true, fallbackMessage = '操作失败，请稍后重试' } = options

  // 记录到控制台（开发模式）
  if (import.meta.env.DEV) {
    console.error('[Error]', error)
  }

  // 用户提示
  if (showMessage) {
    const message = error?.response?.data?.error?.message || error.message || fallbackMessage
    ElMessage.error({
      message,
      duration: 3000,
      showClose: true
    })
  }
}

/**
 * API 请求拦截器中的错误处理
 */
export function setupInterceptors(api) {
  // 响应拦截器
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      const { response } = error

      if (response) {
        switch (response.status) {
          case 401:
            ElMessage.warning('登录已过期，请重新登录')
            // 触发重新登录逻辑
            break
          case 403:
            ElMessage.warning('没有权限执行此操作')
            break
          case 404:
            handleError(new Error('请求的资源不存在'), { showMessage: true })
            break
          case 422:
            const validationMsg = response.data?.error?.details
            ElMessage.warning(validationMsg || '数据验证失败')
            break
          case 502:
            handleError(new Error('第三方服务暂时不可用'), { showMessage: true })
            break
          default:
            handleError(error)
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        ElMessage.error('网络连接失败，请检查网络')
      } else {
        handleError(error)
      }

      return Promise.reject(error)
    }
  )
}
```

#### 2.2 Vue 组件中的标准错误处理

```javascript
// frontend/src/utils/useAsync.js

import { ref } from 'vue'
import { handleError } from './errorHandler'

/**
 * 异步操作封装 Hook
 */
export function useAsync(asyncFn, options = {}) {
  const { immediate = false, onSuccess = null, onError = null } = options

  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function execute(...args) {
    loading.value = true
    error.value = null

    try {
      const result = await asyncFn(...args)
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e
      handleError(e, { showMessage: true })
      onError?.(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    execute()
  }

  return {
    data,
    loading,
    error,
    execute
  }
}

// 使用示例
// const { data: userInfo, loading, execute: fetchUser } = useAsync(() => api.getUser(1))
```

---

## 日志记录规范

### 1. 后端日志（Python）

#### 1.1 日志配置

```python
# backend/app/utils/logging.py

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config import settings

# 日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)8s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """创建配置好的Logger实例"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出（按大小轮转）
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

# 各模块 Logger
app_logger = setup_logger("app")
xfyun_logger = setup_logger("xfyun")
api_logger = setup_logger("api")
db_logger = setup_logger("database")
```

#### 1.2 日志使用规范

```python
# backend/app/services/xinghuo_service.py

import logging
logger = logging.getLogger("xfyun")  # 使用专用logger

class XingHuoService:
    def __init__(self):
        self.logger = logging.getLogger("xfyun")
        self.app_id = settings.XFYUN_APP_ID

    async def chat_completion(self, messages: List[Dict]) -> str:
        # ✅ INFO: 记录正常流程
        self.logger.info(f"[XingHuo] chat_completion called with {len(messages)} messages")

        try:
            result = await self._do_request(messages)
            self.logger.info(f"[XingHuo] Chat success, response length: {len(result)}")
            return result
        except Exception as e:
            # ❌ ERROR: 记录错误及上下文
            self.logger.error(
                f"[XingHuo] Chat failed: {str(e)}",
                exc_info=True,  # 包含堆栈信息
                extra={"messages_count": len(messages)}
            )
            raise

    async def _do_request(self, messages):
        # ✅ DEBUG: 记录调试信息
        self.logger.debug(f"[XingHuo] Request payload: {messages[:2]}...")  # 只打印前两条
        # ...
```

#### 1.3 API 请求日志中间件

```python
# backend/app/utils/logging.py

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", generate_request_id())
        request.state.request_id = request_id

        start_time = time.time()

        # 记录请求
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host}"
        )

        try:
            response = await call_next(request)

            # 记录响应
            duration = time.time() - start_time
            logger.info(
                f"[{request_id}] Response {response.status_code} "
                f"in {duration:.3f}s"
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] Request failed after {duration:.3f}s: {str(e)}",
                exc_info=True
            )
            raise
```

### 2. 前端日志

```javascript
// frontend/src/utils/logger.js

/**
 * 前端日志工具
 * 生产环境只记录 warning 和 error
 */
const logger = {
  _isDev: import.meta.env.DEV,

  debug(...args) {
    if (this._isDev) {
      console.debug('[DEBUG]', ...args)
    }
  },

  info(...args) {
    if (this._isDev) {
      console.info('[INFO]', ...args)
    }
  },

  warn(...args) {
    console.warn('[WARN]', ...args)
  },

  error(...args) {
    console.error('[ERROR]', ...args)
    // 生产环境可上报到错误监控服务
  }
}

export default logger
```

```javascript
// frontend/src/utils/request.js

import axios from 'axios'
import logger from './logger'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    logger.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    // 添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    logger.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

export default api
```

---

## API 设计规范

### 1. RESTful 命名

| 操作 | 方法 | URL模式 | 示例 |
|-----|------|--------|------|
| 获取列表 | GET | `/api/{resource}` | `GET /api/courses` |
| 获取单个 | GET | `/api/{resource}/{id}` | `GET /api/courses/1` |
| 创建 | POST | `/api/{resource}` | `POST /api/courses` |
| 更新 | PUT | `/api/{resource}/{id}` | `PUT /api/courses/1` |
| 删除 | DELETE | `/api/{resource}/{id}` | `DELETE /api/courses/1` |
| 批量操作 | POST | `/api/{resource}/batch` | `POST /api/courses/batch` |

### 2. 响应格式

```python
# 成功响应
{
  "success": true,
  "data": { ... },           # 数据（单个）或 [ ... ]（列表）
  "message": "操作成功",
  "meta": {                  # 可选：分页等元信息
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}

# 错误响应
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "资源不存在",
    "details": { ... }       # 可选：额外错误信息
  }
}
```

### 3. 分页规范

```
GET /api/courses?page=1&page_size=20&sort=created_at&order=desc
```

---

## 数据库规范

### 1. 表命名

- 使用英文小写 + 下划线：`courses`, `student_profiles`
- 表名前缀按模块：`chat_`（对话模块）、`review_`（录音回顾模块）

### 2. 字段命名

- 使用英文小写 + 下划线：`created_at`, `is_active`
- 时间字段：`created_at`, `updated_at`, `deleted_at`（软删除）
- 外键：`{table}_id`，如 `user_id`, `course_id`

### 3. 索引规范

- 主键自动有索引
- 外键必须建立索引
- 频繁查询的字段组合建立复合索引
- 避免过多索引（影响写入性能）

### 4. 软删除

```python
class BaseModel(Base):
    """所有模型的基类，包含公共字段"""
    id = Column(Int, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)  # 软删除标记

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        """按ID查询（排除已删除）"""
        return db.query(cls).filter(cls.id == id, cls.is_deleted == False).first()
```

---

## 代码质量规范

### 1. 后端（Python）

```python
# ✅ 好的实践
from typing import List, Optional, Dict, Any
from app.schemas import UserCreate, UserResponse  # 从 schemas 导入
from app.utils.errors import ValidationException  # 使用统一错误
from app.utils.logging import logger             # 使用专用 logger

class UserService:
    """用户服务类"""

    async def get_user_courses(
        self,
        db: Session,
        user_id: int,
        day_of_week: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户的课程列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            day_of_week: 可选的周几筛选

        Returns:
            课程列表

        Raises:
            NotFoundException: 用户不存在
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User", user_id)

        query = db.query(Course).filter(Course.user_id == user_id)

        if day_of_week is not None:
            query = query.filter(Course.day_of_week == day_of_week)

        return query.all()
```

### 2. 前端（Vue.js）

```javascript
// ✅ 好的实践
// frontend/src/api/timetable.js - 一个模块一个文件

import api from '@/utils/request'

/**
 * 获取今日课程
 * @returns {Promise<{courses: Array, schedules: Array}>}
 */
export function getTodayCourses() {
  return api.get('/timetable/today')
}

/**
 * 导入课表
 * @param {File} imageFile - 课表图片文件
 * @returns {Promise<{message: string, courses: string[]}>}
 */
export function importTimetable(imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  return api.post('/timetable/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
```

---

## Git 提交规范

```
<type>(<scope>): <subject>

类型：
  feat: 新功能
  fix: 修复 bug
  docs: 文档更新
  style: 代码格式（不影响功能）
  refactor: 重构
  test: 测试相关
  chore: 构建/工具相关

示例：
  feat(timetable): 添加课表OCR导入功能
  fix(chat): 修复语音输入时白屏问题
  docs(api): 更新API接口文档
  refactor(xinghuo): 统一讯飞服务错误处理
```

---

## 环境变量规范

```bash
# .env.example

# 数据库（必填）
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/ai_xiaoshang

# 讯飞开放平台（必填）
XFYUN_APP_ID=your_app_id
XFYUN_API_KEY=your_api_key
XFYUN_API_SECRET=your_api_secret

# JWT（必填）
SECRET_KEY=change-this-to-a-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 文件上传（必填）
UPLOAD_DIR=uploads
MAX_AUDIO_SIZE_MB=50
MAX_IMAGE_SIZE_MB=5

# 服务器（可选）
HOST=0.0.0.0
PORT=8000
```

---

## 讯飞 API 使用规范

### 1. 调用原则

| 原则 | 说明 |
|-----|-----|
| 重试机制 | 任何讯飞API调用必须支持3次重试，间隔递增 |
| 超时处理 | 单次调用超时设置为30秒 |
| 鉴权安全 | API Key 只存储在后端，不暴露到前端 |
| 降级方案 | API失败时必须返回友好提示，不能直接报500 |
| 调用统计 | 所有API调用记录日志（成功/失败/耗时） |

### 2. 调用矩阵

| 功能 | API | 调用时机 | 重试 |
|-----|-----|--------|-----|
| 语音输入 | ASR | 用户按住麦克风 | ✅ |
| 录音转写 | ASR(file) | 用户上传MP3 | ✅ |
| 语音播报 | TTS | 用户点击播放 | ✅ |
| 课表识别 | OCR | 用户上传课表图片 | ✅ |
| AI对话 | 星火chat | 用户发送消息 | ✅ |
| 课程总结 | 星火chat | 转写完成后 | ✅ |
| 情感分析 | NLP SA | 用户发送消息时 | ✅ |
| 意图解析 | 星火chat | 用户添加日程时 | ✅ |

---

## 开发工作流

### 1. 每日开发流程

```
1. git pull origin main（拉取最新代码）
2. npm run dev / uvicorn app.main:app --reload（启动开发服务器）
3. 编写代码
4. 手动测试关键功能
5. git add . && git commit -m "feat(scope): 具体描述"
6. （可选）推送到远程
```

### 2. 提交前检查

- [ ] 代码符合本规范的文件结构和命名
- [ ] 所有 API 调用有错误处理
- [ ] 所有错误有日志记录
- [ ] 讯飞 API 调用有重试机制
- [ ] 新功能有对应的文档更新

---

## 文档维护

所有文档统一在 `docs/` 目录下维护，修改代码时同步更新文档。

| 文档 | 更新时机 |
|-----|---------|
| `技术方案.md` | 新增功能模块、修改架构 |
| `接口规范.md` | 新增/修改 API |
| `数据库设计.md` | 新增/修改数据表 |
| `前端开发指南.md` | 新增/修改组件 |
| `后端开发指南.md` | 新增/修改服务 |
| `部署运维.md` | 部署流程变更 |

---

> 最后更新：2026年4月17日
> 维护者：AI小商开发团队
