<template>
  <div class="admin-logs">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          操作日志
        </h1>
        <p class="page-subtitle">审计所有管理员操作记录</p>
      </div>
      <div class="header-actions">
        <el-button @click="router.push('/login')">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button type="primary" :loading="analyzing" @click="handleAIAnalyze" class="ai-btn">
          <el-icon v-if="!analyzing"><MagicStick /></el-icon>
          AI智能分析
        </el-button>
      </div>
    </div>

    <!-- AI分析结果卡片 -->
    <div v-if="analysisResult" class="analysis-card">
      <div class="analysis-header">
        <div class="analysis-title">
          <el-icon><DataAnalysis /></el-icon>
          AI行为分析报告
        </div>
        <el-button text @click="analysisResult = null">收起</el-button>
      </div>
      <div class="analysis-body">
        <div class="analysis-summary">{{ analysisResult.summary }}</div>
        <div class="analysis-grid">
          <div class="analysis-stat">
            <div class="stat-num">{{ analysisResult.total_count || 0 }}</div>
            <div class="stat-label">总操作次数</div>
          </div>
          <div class="analysis-stat">
            <div class="stat-num">{{ analysisResult.peak_hour || 0 }}:00</div>
            <div class="stat-label">高峰时段</div>
          </div>
          <div class="analysis-stat">
            <div class="stat-num">{{ analysisResult.active_days || 0 }}</div>
            <div class="stat-label">活跃天数</div>
          </div>
        </div>
        <div class="top-actions">
          <div class="top-actions-title">操作类型分布</div>
          <div class="top-actions-list">
            <div v-for="(item, idx) in analysisResult.top_actions" :key="idx" class="top-action-item">
              <span class="action-rank">{{ idx + 1 }}</span>
              <span class="action-name">{{ item.action_text }}</span>
              <span class="action-count">{{ item.count }}次</span>
              <div class="action-bar" :style="{ width: (item.count / (analysisResult.top_actions[0]?.count || 1) * 100) + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="trend-section">
          <div class="trend-title">7日操作趋势</div>
          <div ref="trendChartRef" class="trend-chart"></div>
        </div>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-card">
      <div class="quick-filters">
        <el-tag
          v-for="filter in quickFilters"
          :key="filter.value"
          :type="filters.action === filter.value ? 'primary' : 'info'"
          :hit="filters.action === filter.value"
          class="quick-tag"
          @click="handleQuickFilter(filter.value)"
        >
          {{ filter.label }}
        </el-tag>
      </div>
      <div class="filter-row">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
        />
        <el-select v-model="filters.action" placeholder="操作类型" clearable @change="handleFilterChange">
          <el-option v-for="item in actionTypes" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.admin_id" placeholder="管理员" clearable @change="handleFilterChange">
          <el-option v-for="admin in adminList" :key="admin.id" :label="admin.nickname" :value="admin.id" />
        </el-select>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleRefresh">刷新</el-button>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="logs-card">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="created_at" label="操作时间" width="150">
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="admin_name" label="管理员" width="120">
          <template #default="{ row }">
            <div class="admin-info">
              <el-avatar size="small" class="admin-avatar">{{ row.admin_name?.[0] || 'A' }}</el-avatar>
              <span class="admin-name">{{ row.admin_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="action_text" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" size="small">{{ row.action_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作详情" min-width="280">
          <template #default="{ row }">
            <div class="detail-text">{{ formatDetail(row) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130">
          <template #default="{ row }">
            <code class="ip-code">{{ row.ip_address || '-' }}</code>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-card">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { MagicStick, Document, DataAnalysis, ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getLogs, getLogActions, analyzeLogs } from '@/api/admin/log'
import logger from '@/utils/logger'

const router = useRouter()

const quickFilters = [
  { label: '全部', value: '' },
  { label: '禁用', value: 'user.disable' },
  { label: '启用', value: 'user.enable' },
  { label: '登录', value: 'login' },
  { label: '登出', value: 'logout' }
]

const analyzing = ref(false)
const analysisResult = ref(null)
const trendChartRef = ref(null)
const logs = ref([])
const loading = ref(false)
const dateRange = ref([])

const filters = reactive({
  start_date: '',
  end_date: '',
  action: '',
  admin_id: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const actionTypes = ref([])
const adminList = ref([])

function handleQuickFilter(value) {
  filters.action = value
  pagination.page = 1
  fetchLogs()
}

async function handleAIAnalyze() {
  analyzing.value = true
  try {
    const res = await analyzeLogs()
    analysisResult.value = res.data?.data || res.data || {}
    setTimeout(() => initTrendChart(), 100)
  } catch (error) {
    ElMessage.error('AI分析失败')
  } finally {
    analyzing.value = false
  }
}

function initTrendChart() {
  if (!trendChartRef.value || !analysisResult.value?.trend) return
  const chart = echarts.init(trendChartRef.value)
  const trend = analysisResult.value.trend
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trend.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#64748B' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#64748B' },
      splitLine: { lineStyle: { color: '#F1F5F9' } }
    },
    series: [{
      type: 'line',
      data: trend.map(d => d.count),
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(8, 145, 178, 0.3)' },
            { offset: 1, color: 'rgba(8, 145, 178, 0.05)' }
          ]
        }
      },
      lineStyle: { color: '#0891B2', width: 2 },
      itemStyle: { color: '#0891B2' },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

function formatTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 86400000)
  const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())

  if (dateOnly.getTime() === today.getTime()) {
    return `今天 ${date.toTimeString().slice(0, 8)}`
  } else if (dateOnly.getTime() === yesterday.getTime()) {
    return `昨天 ${date.toTimeString().slice(0, 8)}`
  }
  return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.toTimeString().slice(0, 8)}`
}

function getActionTagType(action) {
  if (action?.includes('disable')) return 'danger'
  if (action?.includes('enable')) return 'success'
  if (action?.includes('export')) return 'warning'
  if (action?.includes('login')) return 'info'
  return ''
}

function formatDetail(row) {
  if (!row.detail) return '-'

  // Parse JSON detail if it's a string
  let detail = row.detail
  if (typeof detail === 'string') {
    try {
      detail = JSON.parse(detail)
    } catch {
      return detail
    }
  }

  if (row.action === 'user.disable') {
    const reason = detail?.reason || ''
    return reason ? `禁用用户 #${row.target_id}，原因：${reason}` : `禁用用户 #${row.target_id}`
  }
  if (row.action === 'user.enable') {
    return `启用用户 #${row.target_id}`
  }
  if (row.action === 'user.export') {
    const count = detail?.count || ''
    return count ? `导出用户数据，共${count}条` : `导出用户数据`
  }
  if (row.action === 'user.view') {
    return `查看用户ID #${row.target_id}的详情`
  }
  if (row.action === 'login') {
    return '管理员登录系统'
  }
  if (row.action === 'logout') {
    return '管理员退出登录'
  }
  if (row.action === 'dashboard.view') {
    return '查看数据驾驶舱'
  }
  if (row.action === 'log.view') {
    return '查看操作日志'
  }
  if (typeof row.detail === 'object') {
    return Object.entries(row.detail).map(([k, v]) => `${k}: ${v}`).join('，')
  }
  return String(row.detail)
}

async function fetchLogs() {
  loading.value = true
  try {
    const res = await getLogs({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    })
    const data = res.data?.data || res.data || {}
    logs.value = data.items || []
    pagination.total = data.total || 0

    if (logs.value.length > 0) {
      const adminMap = new Map()
      logs.value.forEach(log => {
        if (log.admin_id && !adminMap.has(log.admin_id)) {
          adminMap.set(log.admin_id, { id: log.admin_id, nickname: log.admin_name })
        }
      })
      adminList.value = Array.from(adminMap.values())
    }
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchActionTypes() {
  try {
    const res = await getLogActions()
    actionTypes.value = res.data?.data || res.data || []
  } catch (error) {
    logger.error('Failed to fetch action types')
  }
}

function handleDateChange(val) {
  filters.start_date = val?.[0] || ''
  filters.end_date = val?.[1] || ''
  pagination.page = 1
  fetchLogs()
}

function handleFilterChange() {
  pagination.page = 1
  fetchLogs()
}

function handleReset() {
  dateRange.value = []
  filters.start_date = ''
  filters.end_date = ''
  filters.action = ''
  filters.admin_id = ''
  fetchLogs()
}

function handleRefresh() {
  fetchLogs()
}

function handlePageChange(page) {
  pagination.page = page
  fetchLogs()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchLogs()
}

onMounted(() => {
  fetchActionTypes()
  fetchLogs()
})
</script>

<style scoped>
.admin-logs {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面标题区 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: #FFFFFF;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.page-title .el-icon {
  color: #0891B2;
  font-size: 28px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.ai-btn {
  padding: 12px 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
}

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
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.analysis-title .el-icon {
  color: #0891B2;
  font-size: 22px;
}

.analysis-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-summary {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 12px;
  border-left: 4px solid #0891B2;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.analysis-stat {
  background: #F8FAFC;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #0891B2;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #64748B;
  margin-top: 8px;
}

.top-actions {
  background: #F8FAFC;
  padding: 20px;
  border-radius: 12px;
}

.top-actions-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 16px;
}

.top-actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.top-action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.action-rank {
  width: 20px;
  height: 20px;
  background: #0891B2;
  color: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.action-name {
  font-size: 14px;
  color: #475569;
  width: 100px;
}

.action-count {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-left: auto;
}

.action-bar {
  position: absolute;
  bottom: -4px;
  left: 32px;
  height: 4px;
  background: linear-gradient(90deg, #0891B2, #22D3EE);
  border-radius: 2px;
  max-width: 120px;
}

.trend-section {
  background: #F8FAFC;
  padding: 20px;
  border-radius: 12px;
}

.trend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 16px;
}

.trend-chart {
  height: 160px;
}

/* 筛选工具栏 */
.filter-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.quick-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F1F5F9;
}

.quick-tag {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  transition: all 0.2s;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-row .el-date-picker {
  width: 260px;
}

.filter-row .el-select {
  width: 140px;
}

/* 日志卡片 */
.logs-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.time-text {
  font-size: 14px;
  color: #475569;
  font-family: 'JetBrains Mono', monospace;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-avatar {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  font-size: 12px;
  color: #FFFFFF;
}

.admin-name {
  font-size: 14px;
  color: #1E293B;
  font-weight: 500;
}

.detail-text {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
}

.ip-code {
  font-size: 13px;
  color: #64748B;
  font-family: 'JetBrains Mono', monospace;
  background: #F8FAFC;
  padding: 4px 8px;
  border-radius: 6px;
}

/* 分页 */
.pagination-card {
  background: #FFFFFF;
  padding: 16px 20px;
  border-radius: 16px;
  margin-top: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .analysis-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .filter-row {
    flex-direction: column;
  }

  .filter-row .el-date-picker,
  .filter-row .el-select {
    width: 100%;
  }
}
</style>
