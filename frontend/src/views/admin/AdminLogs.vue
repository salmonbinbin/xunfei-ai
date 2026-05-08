<template>
  <div class="admin-logs">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          操作日志
        </h1>
        <p class="page-subtitle">审计所有管理员操作记录</p>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-bar">
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
          <el-option
            v-for="item in actionTypes"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <el-select v-model="filters.admin_id" placeholder="管理员" clearable @change="handleFilterChange">
          <el-option
            v-for="admin in adminList"
            :key="admin.id"
            :label="admin.nickname"
            :value="admin.id"
          />
        </el-select>
      </div>

      <div class="filter-actions">
        <el-button @click="handleReset">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
          </svg>
          重置
        </el-button>
        <el-button @click="handleRefresh">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"/>
            <path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="logs-table">
      <el-table
        :data="logs"
        v-loading="loading"
        stripe
      >
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            <span class="time-cell">{{ row.created_at }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="admin_name" label="管理员" width="120">
          <template #default="{ row }">
            <div class="admin-cell">
              <div class="admin-avatar">{{ row.admin_name?.[0] || 'A' }}</div>
              <span>{{ row.admin_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="action_text" label="操作类型" width="140">
          <template #default="{ row }">
            <span class="action-badge" :class="getActionClass(row.action)">
              {{ row.action_text }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作详情" min-width="200">
          <template #default="{ row }">
            <div class="detail-cell">
              <span class="target-info" v-if="row.target_type">
                {{ row.target_type }} #{{ row.target_id }}
              </span>
              <span class="detail-info" v-if="row.detail">
                {{ formatDetail(row.detail) }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140">
          <template #default="{ row }">
            <span class="ip-cell">{{ row.ip_address || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLogs, getLogActions } from '@/api/admin/log'
import logger from '@/utils/logger'

// 日志列表数据
const logs = ref([])

// 加载状态
const loading = ref(false)

// 日期范围
const dateRange = ref([])

// 筛选条件
const filters = reactive({
  start_date: '',
  end_date: '',
  action: '',
  admin_id: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 操作类型选项
const actionTypes = ref([])

// 管理员列表（从日志中提取）
const adminList = ref([])

// 获取日志列表
async function fetchLogs() {
  loading.value = true
  logger.info('[AdminLogs] Fetching logs with filters:', filters)

  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    const res = await getLogs(params)

    const data = res.data?.data || res.data || {}
    logs.value = data.items || []
    pagination.total = data.total || 0

    // 提取管理员列表
    if (logs.value.length > 0) {
      const adminMap = new Map()
      logs.value.forEach(log => {
        if (log.admin_id && !adminMap.has(log.admin_id)) {
          adminMap.set(log.admin_id, { id: log.admin_id, nickname: log.admin_name })
        }
      })
      adminList.value = Array.from(adminMap.values())
    }

    logger.info('[AdminLogs] Logs fetched:', logs.value.length)
  } catch (error) {
    logger.error('[AdminLogs] Failed to fetch logs:', error?.response?.data || error.message)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

// 获取操作类型枚举
async function fetchActionTypes() {
  try {
    const res = await getLogActions()
    actionTypes.value = res.data?.data || res.data || []
    logger.debug('[AdminLogs] Action types loaded:', actionTypes.value.length)
  } catch (error) {
    logger.error('[AdminLogs] Failed to fetch action types:', error.message)
  }
}

// 日期变化
function handleDateChange(val) {
  if (val && val.length === 2) {
    filters.start_date = val[0]
    filters.end_date = val[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  pagination.page = 1
  fetchLogs()
}

// 筛选变化
function handleFilterChange() {
  pagination.page = 1
  fetchLogs()
}

// 重置
function handleReset() {
  dateRange.value = []
  filters.start_date = ''
  filters.end_date = ''
  filters.action = ''
  filters.admin_id = ''
  pagination.page = 1
  fetchLogs()
}

// 刷新
function handleRefresh() {
  fetchLogs()
}

// 分页变化
function handlePageChange(page) {
  pagination.page = page
  fetchLogs()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchLogs()
}

// 获取操作样式类
function getActionClass(action) {
  if (action?.includes('disable')) return 'danger'
  if (action?.includes('enable')) return 'success'
  if (action?.includes('export')) return 'info'
  if (action?.includes('view')) return 'default'
  return 'default'
}

// 格式化详情
function formatDetail(detail) {
  if (!detail) return ''
  if (typeof detail === 'string') return detail
  try {
    return JSON.stringify(detail)
  } catch {
    return String(detail)
  }
}

onMounted(() => {
  logger.debug('[AdminLogs] Component mounted')
  fetchActionTypes()
  fetchLogs()
})
</script>

<style scoped>
/* ============================================
   AI小商 管理端操作日志页面
   设计风格: 深色科技风 + 数据表格
   ============================================ */

:root {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --success: #059669;
  --danger: #EF4444;
  --info: #0284C7;
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --bg-card-hover: #273549;
  --border-color: #334155;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
}

.admin-logs {
  max-width: 1600px;
  margin: 0 auto;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
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

/* 筛选工具栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-row :deep(.el-date-editor) {
  width: 260px;
}

.filter-row :deep(.el-select) {
  width: 140px;
}

.filter-row :deep(.el-input__wrapper) {
  background: var(--bg-dark);
  border-color: var(--border-color);
  box-shadow: none;
}

.filter-row :deep(.el-range-input) {
  color: var(--text-primary);
}

.filter-actions {
  display: flex;
  gap: 12px;
}

.filter-actions :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-dark);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

.filter-actions :deep(.el-button:hover) {
  background: var(--bg-card-hover);
  border-color: var(--primary);
  color: var(--text-primary);
}

.filter-actions :deep(.el-button svg) {
  width: 16px;
  height: 16px;
}

/* 日志表格 */
.logs-table {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.logs-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255, 255, 255, 0.02);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.03);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-muted);
}

.logs-table :deep(.el-table th) {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.logs-table :deep(.el-table td) {
  padding: 16px 12px;
}

.time-cell {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--text-secondary);
}

.admin-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.action-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.action-badge.default {
  background: rgba(148, 163, 184, 0.1);
  color: var(--text-secondary);
}

.action-badge.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.action-badge.success {
  background: rgba(5, 150, 105, 0.1);
  color: var(--success);
}

.action-badge.info {
  background: rgba(2, 132, 199, 0.1);
  color: var(--info);
}

.detail-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.target-info {
  font-size: 13px;
  color: var(--text-muted);
}

.detail-info {
  font-size: 12px;
  color: var(--text-muted);
  word-break: break-all;
}

.ip-cell {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-muted);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 16px 16px;
}

.pagination-wrapper :deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-bg-color: var(--bg-dark);
  --el-pagination-button-color: var(--text-secondary);
  --el-pagination-hover-color: var(--primary);
}

.pagination-wrapper :deep(.el-pager li) {
  background: var(--bg-dark);
  border-radius: 8px;
}

.pagination-wrapper :deep(.el-pager li.is-active) {
  background: var(--primary);
  color: white;
}

/* 日期选择器样式 */
:deep(.el-date-editor.el-input__wrapper) {
  background: var(--bg-dark);
  border-color: var(--border-color);
}

:deep(.el-range-separator) {
  color: var(--text-muted);
}
</style>