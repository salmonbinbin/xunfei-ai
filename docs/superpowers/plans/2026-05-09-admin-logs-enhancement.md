# 管理端操作日志增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强管理端操作日志模块，实现清晰明了的日志展示 + AI智能分析辅助功能

**Architecture:**
- 前端AdminLogs.vue页面改造：快捷筛选按钮、时间分级显示、操作类型彩色标签、AI分析卡片
- 后端新增 `/api/admin/logs/analyze` 端点，调用星火API分析最近7天日志
- API返回结构化数据（摘要、总次数、TOP操作、高峰时段、7天趋势）

**Tech Stack:** Vue3 + Element Plus + ECharts / FastAPI + SQLAlchemy + 讯飞星火大模型

---

## 文件结构

```
backend/app/
├── routers/admin_console/
│   └── log.py                    # 修改：新增 /analyze 端点
├── services/
│   └── xinghuo_service.py        # 复用：chat_completion 方法

frontend/src/
├── api/admin/
│   └── log.js                    # 修改：新增 analyzeLogs API
├── views/admin/
│   └── AdminLogs.vue            # 修改：增强日志展示 + AI分析卡片
└── utils/
    └── echarts.js                # 复用：getLineChartOption
```

---

## 实施任务

### Task 1: 前端API封装 - 新增analyzeLogs

**Files:**
- Modify: `frontend/src/api/admin/log.js`

- [ ] **Step 1: 在 log.js 中新增 analyzeLogs 导出**

```javascript
// 在文件末尾添加
export const analyzeLogs = () => {
  logger.debug('[AdminAPI] Analyze logs with AI')
  return adminApi.post('/admin/logs/analyze')
}
```

- [ ] **Step 2: 验证文件语法**

Run: `cd /Users/salmon/Desktop/Xunfei\ project/AI小商/frontend && node -c src/api/admin/log.js`
Expected: 无输出（语法正确）

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/admin/log.js
git commit -m "feat(admin): 新增 analyzeLogs API"
```

---

### Task 2: 后端 - 新增 /analyze 端点

**Files:**
- Modify: `backend/app/routers/admin_console/log.py`
- Test: `backend/app/routers/admin_console/log.py` 中的新端点

- [ ] **Step 1: 在 log.py 末尾添加 analyze 端点**

```python
@router.post("/analyze")
@handle_app_errors
async def analyze_logs(request: Request, db: AsyncSession = Depends(get_db)):
    """AI智能分析最近7天日志"""
    admin_id = get_current_admin_id(request)
    logger.info(f"[Logs] Analyze logs, admin_id={admin_id}")

    # 计算7天前的日期
    from datetime import timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)

    # 查询近7天日志
    query = (
        select(AdminLog)
        .where(AdminLog.created_at >= seven_days_ago)
        .order_by(AdminLog.created_at.desc())
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    # 聚合统计数据
    total_count = len(logs)
    action_counts = {}
    hour_counts = {}

    for log in logs:
        # 统计操作类型
        action = log.action
        action_counts[action] = action_counts.get(action, 0) + 1

        # 统计高峰时段
        if log.created_at:
            hour = log.created_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

    # 计算TOP3操作类型
    top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_actions = [
        {"action": action, "action_text": get_action_text(action), "count": count}
        for action, count in top_actions
    ]

    # 计算高峰时段
    peak_hour = max(hour_counts.keys(), key=lambda h: hour_counts[h]) if hour_counts else 9

    # 计算7天趋势
    trend = []
    for i in range(7):
        day = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        count = sum(1 for log in logs if log.created_at and log.created_at.strftime('%Y-%m-%d') == day)
        trend.append({"date": day, "count": count})

    # 调用星火API生成摘要
    summary = await generate_log_summary(total_count, top_actions, peak_hour)

    return {
        "success": True,
        "data": {
            "summary": summary,
            "total_count": total_count,
            "top_actions": top_actions,
            "peak_hour": peak_hour,
            "trend": trend
        }
    }


def get_action_text(action: str) -> str:
    """获取操作类型的中文描述"""
    action_map = {
        "login": "管理员登录",
        "logout": "管理员登出",
        "user.disable": "禁用用户",
        "user.enable": "启用用户",
        "user.export": "导出用户数据",
        "user.view": "查看用户",
        "log.view": "查看操作日志",
        "dashboard.view": "查看数据看板"
    }
    return action_map.get(action, action)


async def generate_log_summary(total_count: int, top_actions: list, peak_hour: int) -> str:
    """调用星火API生成日志摘要"""
    from app.services.xinghuo_service import XingHuoService

    if total_count == 0:
        return "近7天无操作记录"

    # 构建统计数据文本
    action_texts = [f"{a['action_text']}：{a['count']}次" for a in top_actions]
    stats_text = f"总操作{total_count}次，{'，'.join(action_texts)}，高峰时段{peak_hour}:00-{peak_hour+1}:00"

    prompt = f"""你是一个数据分析助手。请根据以下统计数据，用简洁的语言（50字以内）描述管理员的操作特点。

统计数据：
{stats_text}

请直接输出一段简短的总结，不要其他解释。"""

    try:
        service = XingHuoService()
        messages = [{"role": "user", "content": prompt}]
        result = await service.chat_completion(messages, user_id="admin")
        return result.strip() if result else stats_text
    except Exception as e:
        logger.error(f"[Logs] Failed to generate summary: {e}")
        return stats_text
```

- [ ] **Step 2: 验证语法**

Run: `cd /Users/salmon/Desktop/Xunfei\ project/AI小商/backend && python3 -m py_compile app/routers/admin_console/log.py`
Expected: 无输出（语法正确）

- [ ] **Step 3: 测试端点**

Run:
```bash
curl -X POST http://localhost:8000/api/admin/logs/analyze \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:8000/api/admin/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"123456"}' | jq -r '.data.token')"
```
Expected: JSON响应包含 summary, total_count, top_actions, peak_hour, trend

- [ ] **Step 4: 提交**

```bash
git add backend/app/routers/admin_console/log.py
git commit -m "feat(admin): 新增日志分析API /analyze"
```

---

### Task 3: 前端 - AdminLogs.vue 页面改造

**Files:**
- Modify: `frontend/src/views/admin/AdminLogs.vue`

- [ ] **Step 1: 添加快捷筛选按钮和AI分析按钮（template部分）**

在页面标题区域添加AI分析按钮：
```html
<div class="page-header">
  <div class="header-content">
    <h1 class="page-title">操作日志</h1>
    <p class="page-subtitle">审计所有管理员操作记录</p>
  </div>
  <el-button type="primary" @click="handleAIAnalyze" :loading="analyzing">
    <el-icon><Magic /></el-icon>
    AI智能分析
  </el-button>
</div>
```

添加快捷筛选按钮（在筛选工具栏顶部）：
```html
<div class="quick-filters">
  <el-button
    v-for="item in quickFilters"
    :key="item.value"
    :type="filters.action === item.value ? 'primary' : ''"
    size="small"
    @click="handleQuickFilter(item.value)"
  >
    {{ item.label }}
  </el-button>
</div>
```

- [ ] **Step 2: 添加AI分析结果卡片**

```html
<div v-if="analysisResult" class="analysis-card">
  <div class="analysis-header">
    <span class="analysis-title">AI行为分析</span>
    <el-button text @click="analysisResult = null">收起</el-button>
  </div>
  <div class="analysis-content">
    <div class="analysis-summary">{{ analysisResult.summary }}</div>
    <div class="analysis-stats">
      <div class="stat-item">
        <span class="stat-value">{{ analysisResult.total_count }}</span>
        <span class="stat-label">总操作</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ analysisResult.peak_hour }}:00</span>
        <span class="stat-label">高峰时段</span>
      </div>
    </div>
    <div ref="trendChartRef" class="trend-chart"></div>
  </div>
</div>
```

- [ ] **Step 3: 添加script setup中的相关变量和方法**

```javascript
import { Magic } from '@element-plus/icons-vue'
import { analyzeLogs } from '@/api/admin/log'
import { getLineChartOption } from '@/utils/echarts'
import * as echarts from 'echarts'

const quickFilters = [
  { label: '全部', value: '' },
  { label: '禁用', value: 'user.disable' },
  { label: '启用', value: 'user.enable' },
  { label: '导出', value: 'user.export' },
  { label: '登录', value: 'login' }
]

const analyzing = ref(false)
const analysisResult = ref(null)
const trendChartRef = ref(null)

function handleQuickFilter(value) {
  filters.action = value
  pagination.page = 1
  fetchLogs()
}

async function handleAIAnalyze() {
  analyzing.value = true
  try {
    const res = await analyzeLogs()
    analysisResult.value = res.data.data
    setTimeout(() => {
      const chart = echarts.init(trendChartRef.value)
      chart.setOption(getLineChartOption(
        analysisResult.value.trend.map(t => ({
          hour: t.date.slice(5),
          count: t.count
        }))
      ))
    }, 100)
  } catch (error) {
    ElMessage.error('分析失败')
  } finally {
    analyzing.value = false
  }
}
```

- [ ] **Step 4: 添加时间格式化函数**

```javascript
function formatTime(timeStr) {
  if (!timeStr) return '-'
  const now = new Date()
  const time = new Date(timeStr)
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86400000)

  if (time >= today) {
    return `今天 ${timeStr.split(' ')[1]}`
  } else if (time >= yesterday) {
    return `昨天 ${timeStr.split(' ')[1]}`
  } else {
    return timeStr.slice(5, 16).replace('T', ' ')
  }
}
```

- [ ] **Step 5: 添加样式**

```css
/* AI分析卡片 */
.analysis-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.analysis-summary {
  font-size: 14px;
  color: #475569;
  margin-bottom: 16px;
  line-height: 1.6;
}

.analysis-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0891B2;
}

.stat-label {
  font-size: 12px;
  color: #94A3B8;
}

.trend-chart {
  height: 150px;
}

/* 快捷筛选按钮 */
.quick-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
```

- [ ] **Step 6: 验证页面可运行**

Run: `cd /Users/salmon/Desktop/Xunfei\ project/AI小商/frontend && npm run dev`
Expected: 开发服务器启动，无编译错误

- [ ] **Step 7: 提交**

```bash
git add frontend/src/views/admin/AdminLogs.vue frontend/src/api/admin/log.js
git commit -m "feat(admin): 操作日志页面增强 - 快捷筛选、AI分析卡片"
```

---

## 验收检查清单

- [ ] 日志列表清晰展示，操作类型一眼可辨
- [ ] 时间格式易读（今天/昨天/日期分级）
- [ ] 快捷筛选按钮一键切换
- [ ] AI分析按钮可点击，加载状态可见
- [ ] 分析结果以卡片形式展示，包含概览和趋势图
- [ ] 7天趋势图正确显示

---

## 已知约束

1. **API路径**: 后端路由使用 `/api/admin/logs/*` 前缀
2. **星火API**: 复用 `XingHuoService.chat_completion` 方法，prompt简短控制成本
3. **样式风格**: 复用现有深色科技风，保持一致性
