<template>
  <div class="admin-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
          数据驾驶舱
        </h1>
        <p class="page-subtitle">实时掌握系统运营状况</p>
      </div>
      <div class="header-actions">
        <button class="refresh-btn" @click="fetchData" :disabled="loading">
          <svg :class="{ 'spin': loading }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"/>
            <path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          <span>{{ loading ? '刷新中...' : '刷新数据' }}</span>
        </button>
        <div class="date-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>{{ currentDate }}</span>
        </div>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="stats-grid">
      <div
        v-for="(stat, index) in statsCards"
        :key="stat.key"
        class="stat-card"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <div class="stat-icon" :class="stat.colorClass">
          <component :is="stat.icon" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value.toLocaleString() }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-trend" v-if="stat.trend !== undefined">
          <svg v-if="stat.trend > 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
          <svg v-else-if="stat.trend < 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
          <span :class="stat.trend > 0 ? 'up' : 'down'">{{ Math.abs(stat.trend) }}%</span>
        </div>
        <div class="stat-bg-icon">
          <component :is="stat.icon" />
        </div>
      </div>
    </div>

    <!-- 用户统计 -->
    <div class="login-stats">
      <div class="login-stat-card student">
        <div class="login-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <div class="login-info">
          <span class="login-value">{{ stats.total_students?.toLocaleString() || 0 }}</span>
          <span class="login-label">学生用户人数</span>
        </div>
        <div class="login-trend up">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
        </div>
      </div>
      <div class="login-stat-card teacher">
        <div class="login-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="login-info">
          <span class="login-value">{{ stats.total_teachers?.toLocaleString() || 0 }}</span>
          <span class="login-label">教师用户人数</span>
        </div>
        <div class="login-trend up">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 功能使用排行 -->
      <div class="chart-card rank-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
            功能使用排行
          </h3>
          <span class="chart-badge">今日</span>
        </div>
        <div class="chart-container bar-chart" ref="barChartRef"></div>
      </div>

      <!-- API调用统计 -->
      <div class="chart-card pie-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
              <path d="M22 12A10 10 0 0 0 12 2v10z"/>
            </svg>
            API调用统计
          </h3>
          <span class="chart-badge">实时</span>
        </div>
        <div class="chart-container pie-chart" ref="pieChartRef"></div>
      </div>

      <!-- 24小时趋势 -->
      <div class="chart-card trend-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            活跃用户趋势
          </h3>
          <span class="chart-badge">24小时</span>
        </div>
        <div class="chart-container line-chart" ref="lineChartRef"></div>
      </div>
    </div>

    <!-- API详细统计 -->
    <div class="api-stats-table">
      <div class="table-header">
        <h3 class="table-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          API调用详情
        </h3>
      </div>
      <div class="table-content">
        <table class="data-table">
          <thead>
            <tr>
              <th>API名称</th>
              <th>调用次数</th>
              <th>失败次数</th>
              <th>失败率</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="api in stats.api_stats || []" :key="api.api_name">
              <td>
                <span class="api-name">{{ api.name }}</span>
                <span class="api-key">{{ api.api_name.toUpperCase() }}</span>
              </td>
              <td>
                <span class="stat-number">{{ api.count?.toLocaleString() || 0 }}</span>
              </td>
              <td>
                <span class="stat-number danger">{{ api.fail_count || 0 }}</span>
              </td>
              <td>
                <div class="progress-bar">
                  <div class="progress-fill" :class="getFailRateClass(api.fail_rate)" :style="{ width: `${api.fail_rate || 0}%` }"></div>
                </div>
                <span class="progress-text">{{ api.fail_rate?.toFixed(2) || 0 }}%</span>
              </td>
              <td>
                <span class="status-badge" :class="getFailRateClass(api.fail_rate)">
                  {{ getStatusText(api.fail_rate) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, h } from 'vue'
import { getDashboardStats, getDashboardTrend } from '@/api/admin/dashboard'
import { getBarChartOption, getPieChartOption, getLineChartOption, getGaugeOption } from '@/utils/adminChart'
import logger from '@/utils/logger'
import * as echarts from 'echarts'

// 统计数据
const stats = reactive({
  today_online_users: 0,
  today_student_logins: 0,
  today_teacher_logins: 0,
  today_api_calls: 0,
  total_students: 0,
  total_teachers: 0,
  api_stats: [],
  module_ranking: []
})

// 小时趋势数据
const hourlyData = ref([])

// 加载状态
const loading = ref(false)

// 图表引用
const barChartRef = ref(null)
const pieChartRef = ref(null)
const lineChartRef = ref(null)

// 图表实例
let barChart = null
let pieChart = null
let lineChart = null

// 刷新定时器
let refreshTimer = null

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

// 指标卡片配置
const statsCards = computed(() => [
  {
    key: 'online_users',
    label: '今日在线人数',
    value: stats.today_online_users || 0,
    colorClass: 'success',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
        h('polyline', { points: '22 4 12 14.01 9 11.01' })
      ])
    }
  },
  {
    key: 'api_calls',
    label: 'API调用总量',
    value: stats.today_api_calls || 0,
    colorClass: 'info',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })
      ])
    }
  },
  {
    key: 'student_logins',
    label: '学生登录数',
    value: stats.today_student_logins || 0,
    colorClass: 'purple',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M22 10v6M2 10l10-5 10 5-10 5z' }),
        h('path', { d: 'M6 12v5c3 3 9 3 12 0v-5' })
      ])
    }
  },
  {
    key: 'teacher_logins',
    label: '教师登录数',
    value: stats.today_teacher_logins || 0,
    colorClass: 'warning',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
        h('circle', { cx: '9', cy: '7', r: '4' }),
        h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
        h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
      ])
    }
  }
])

// 获取失败率样式
function getFailRateClass(rate) {
  if (rate > 5) return 'danger'
  if (rate > 1) return 'warning'
  return 'success'
}

// 获取状态文字
function getStatusText(rate) {
  if (rate > 5) return '异常'
  if (rate > 1) return '警告'
  return '正常'
}

// 初始化图表
function initCharts() {
  logger.debug('[AdminDashboard] Initializing charts...')

  // 柱状图 - 功能使用排行
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    barChart.setOption(getBarChartOption(
      stats.module_ranking?.map(m => ({ name: m.name, value: m.count })) || []
    ))
  }

  // 饼图 - API调用统计
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption(getPieChartOption(
      stats.api_stats?.map(a => ({ name: a.name, value: a.count })) || []
    ))
  }

  // 折线图 - 24小时趋势
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value)
    lineChart.setOption(getLineChartOption(
      hourlyData.value.map(h => ({ hour: h.hour, count: h.user_count }))
    ))
  }
}

// 更新图表数据
function updateCharts() {
  logger.debug('[AdminDashboard] Updating chart data...')

  if (barChart) {
    barChart.setOption(getBarChartOption(
      stats.module_ranking?.map(m => ({ name: m.name, value: m.count })) || []
    ), false)
  }

  if (pieChart) {
    pieChart.setOption(getPieChartOption(
      stats.api_stats?.map(a => ({ name: a.name, value: a.count })) || []
    ), false)
  }

  if (lineChart) {
    lineChart.setOption(getLineChartOption(
      hourlyData.value.map(h => ({ hour: h.hour, count: h.user_count }))
    ), false)
  }
}

// 获取数据
async function fetchData() {
  loading.value = true
  logger.info('[AdminDashboard] Fetching dashboard data...')

  try {
    const [statsRes, trendRes] = await Promise.all([
      getDashboardStats(),
      getDashboardTrend()
    ])

    // 更新统计数据
    const statsData = statsRes.data?.data || statsRes.data || {}
    Object.assign(stats, {
      today_online_users: statsData.today_online_users || 0,
      today_student_logins: statsData.today_student_logins || 0,
      today_teacher_logins: statsData.today_teacher_logins || 0,
      today_api_calls: statsData.today_api_calls || 0,
      total_students: statsData.total_students || 0,
      total_teachers: statsData.total_teachers || 0,
      api_stats: statsData.api_stats || [],
      module_ranking: statsData.module_ranking || []
    })

    // 更新小时趋势数据
    const trendData = trendRes.data?.data || trendRes.data || {}
    hourlyData.value = trendData.hours || []

    logger.info('[AdminDashboard] Data fetched successfully', {
      onlineUsers: stats.today_online_users,
      apiCalls: stats.today_api_calls,
      moduleCount: stats.module_ranking?.length
    })

    // 更新图表
    updateCharts()
  } catch (error) {
    logger.error('[AdminDashboard] Failed to fetch data:', error?.response?.data || error.message)
  } finally {
    loading.value = false
  }
}

// 处理窗口大小变化
function handleResize() {
  barChart?.resize()
  pieChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  logger.info('[AdminDashboard] Component mounted, initializing...')
  fetchData()
  initCharts()

  // 添加窗口大小监听
  window.addEventListener('resize', handleResize)

  // 30秒自动刷新
  refreshTimer = setInterval(fetchData, 30000)

  logger.debug('[AdminDashboard] Dashboard initialized, auto-refresh set to 30s')
})

onUnmounted(() => {
  logger.info('[AdminDashboard] Component unmounting, cleaning up...')

  // 清理图表实例
  barChart?.dispose()
  pieChart?.dispose()
  lineChart?.dispose()

  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }

  // 清理窗口监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ============================================
   AI小商 管理端数据驾驶舱
   设计风格: 深色科技风 + 数据可视化
   ============================================ */

:root {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --success: #059669;
  --warning: #F59E0B;
  --danger: #EF4444;
  --purple: #8B5CF6;
  --cyan: #06B6D4;
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --bg-card-hover: #273549;
  --border-color: #334155;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
}

.admin-dashboard {
  max-width: 1600px;
  margin: 0 auto;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-title svg {
  width: 28px;
  height: 28px;
  color: var(--primary);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--bg-card-hover);
  border-color: var(--primary);
  color: var(--text-primary);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.date-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 10px;
  color: var(--primary-light);
  font-size: 14px;
  font-weight: 500;
}

.date-badge svg {
  width: 16px;
  height: 16px;
}

/* 核心指标卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: var(--primary);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.stat-icon svg {
  width: 26px;
  height: 26px;
}

.stat-icon.primary {
  background: rgba(8, 145, 178, 0.15);
  color: var(--primary);
}

.stat-icon.success {
  background: rgba(5, 150, 105, 0.15);
  color: var(--success);
}

.stat-icon.info {
  background: rgba(6, 182, 212, 0.15);
  color: var(--cyan);
}

.stat-icon.warning {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.stat-icon.purple {
  background: rgba(139, 92, 246, 0.15);
  color: var(--purple);
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up {
  color: var(--success);
}

.stat-trend.down {
  color: var(--danger);
}

.stat-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -10px;
  width: 100px;
  height: 100px;
  opacity: 0.05;
}

.stat-bg-icon svg {
  width: 100%;
  height: 100%;
}

/* 登录统计 */
.login-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.login-stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  animation-delay: 400ms;
}

.login-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-icon svg {
  width: 24px;
  height: 24px;
}

.login-stat-card.student .login-icon {
  background: rgba(8, 145, 178, 0.15);
  color: var(--primary);
}

.login-stat-card.teacher .login-icon {
  background: rgba(139, 92, 246, 0.15);
  color: var(--purple);
}

.login-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.login-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.login-label {
  font-size: 13px;
  color: var(--text-muted);
}

.login-trend {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-trend svg {
  width: 18px;
  height: 18px;
}

.login-trend.up {
  background: rgba(5, 150, 105, 0.15);
  color: var(--success);
}

.login-trend.down {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

.chart-card:nth-child(1) { animation-delay: 200ms; }
.chart-card:nth-child(2) { animation-delay: 300ms; }
.chart-card:nth-child(3) { animation-delay: 400ms; }
.chart-card:nth-child(4) { animation-delay: 500ms; }
.chart-card:nth-child(5) { animation-delay: 600ms; }
.chart-card:nth-child(6) { animation-delay: 700ms; }

.trend-card {
  grid-column: span 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-title svg {
  width: 20px;
  height: 20px;
  color: var(--primary);
}

.chart-badge {
  padding: 4px 12px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  color: var(--primary-light);
}

.chart-badge.danger {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

.chart-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.2);
  color: var(--warning);
}

.chart-badge.success {
  background: rgba(5, 150, 105, 0.1);
  border-color: rgba(5, 150, 105, 0.2);
  color: var(--success);
}

.chart-container {
  height: 280px;
}

.gauge-card .chart-container {
  height: 240px;
}

/* API统计表格 */
.api-stats-table {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  animation-delay: 600ms;
}

.table-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.table-title svg {
  width: 20px;
  height: 20px;
  color: var(--primary);
}

.table-content {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 14px 20px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.api-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.api-key {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.stat-number {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.stat-number.danger {
  color: var(--danger);
}

.progress-bar {
  width: 80px;
  height: 6px;
  background: var(--bg-dark);
  border-radius: 3px;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-fill.success {
  background: var(--success);
}

.progress-fill.warning {
  background: var(--warning);
}

.progress-fill.danger {
  background: var(--danger);
}

.progress-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: rgba(5, 150, 105, 0.1);
  color: var(--success);
}

.status-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.status-badge.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .trend-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .login-stats {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>