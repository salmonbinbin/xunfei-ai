<template>
  <div class="admin-users">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          用户管理中心
        </h1>
        <p class="page-subtitle">管理所有学生和教师账户</p>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-select v-model="filters.role" placeholder="角色" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="学生" value="student" />
          <el-option label="教师" value="teacher" />
        </el-select>

        <el-select v-model="filters.status" placeholder="状态" clearable @change="handleFilterChange">
          <el-option label="全部" value="" />
          <el-option label="正常" value="active" />
          <el-option label="已禁用" value="disabled" />
        </el-select>

        <el-input
          v-model="filters.keyword"
          placeholder="搜索昵称/手机号"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </template>
        </el-input>

        <el-button type="primary" @click="handleSearch">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          搜索
        </el-button>
      </div>

      <div class="filter-actions">
        <el-button @click="handleExport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出Excel
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

    <!-- 用户列表 -->
    <div class="users-table">
      <el-table
        :data="users"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="nickname" label="昵称" min-width="120">
          <template #default="{ row }">
            <div class="user-info">
              <div class="user-avatar">
                {{ row.nickname?.[0] || 'U' }}
              </div>
              <span class="user-name">{{ row.nickname }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130">
          <template #default="{ row }">
            <span class="phone-masked">{{ row.phone }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <span class="role-badge" :class="row.role">
              {{ row.role === 'student' ? '学生' : '教师' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="专业/院系" width="140">
          <template #default="{ row }">
            <span class="major-text">{{ row.major || row.department || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status">
              {{ row.status === 'active' ? '正常' : '已禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160">
          <template #default="{ row }">
            <span class="time-text">{{ row.last_login || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_chats" label="对话次数" width="100" sortable>
          <template #default="{ row }">
            <span class="chat-count">{{ row.total_chats || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              :type="row.status === 'active' ? 'danger' : 'success'"
              size="small"
              text
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
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

    <!-- 状态切换确认对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      :title="statusAction === 'disable' ? '禁用用户' : '启用用户'"
      width="400px"
      align-center
    >
      <div class="dialog-content">
        <p>确定要{{ statusAction === 'disable' ? '禁用' : '启用' }}用户「<strong>{{ currentUser?.nickname }}</strong>」吗？</p>
        <div class="reason-input" v-if="statusAction === 'disable'">
          <label>禁用原因（可选）：</label>
          <el-input v-model="statusReason" type="textarea" placeholder="请输入禁用原因" />
        </div>
      </div>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button :type="statusAction === 'disable' ? 'danger' : 'primary'" @click="confirmStatusChange">
          确认{{ statusAction === 'disable' ? '禁用' : '启用' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, updateUserStatus, exportUsers } from '@/api/admin/user'
import logger from '@/utils/logger'

// 用户列表数据
const users = ref([])

// 加载状态
const loading = ref(false)

// 筛选条件
const filters = reactive({
  role: '',
  status: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 状态切换对话框
const statusDialogVisible = ref(false)
const statusAction = ref('disable')
const currentUser = ref(null)
const statusReason = ref('')

// 选中行
const selectedRows = ref([])

// 获取用户列表
async function fetchUsers() {
  loading.value = true
  logger.info('[AdminUsers] Fetching users with filters:', filters)

  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    const res = await getUsers(params)

    const data = res.data?.data || res.data || {}
    users.value = data.items || []
    pagination.total = data.total || 0

    logger.info('[AdminUsers] Users fetched:', users.value.length)
  } catch (error) {
    logger.error('[AdminUsers] Failed to fetch users:', error?.response?.data || error.message)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选变化
function handleFilterChange() {
  pagination.page = 1
  fetchUsers()
}

// 搜索
function handleSearch() {
  pagination.page = 1
  fetchUsers()
}

// 刷新
function handleRefresh() {
  fetchUsers()
}

// 分页变化
function handlePageChange(page) {
  pagination.page = page
  fetchUsers()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchUsers()
}

// 选择变化
function handleSelectionChange(selection) {
  selectedRows.value = selection
}

// 切换用户状态
function handleToggleStatus(user) {
  currentUser.value = user
  statusAction.value = user.status === 'active' ? 'disable' : 'enable'
  statusReason.value = ''
  statusDialogVisible.value = true
}

// 确认状态切换
async function confirmStatusChange() {
  if (!currentUser.value) return

  const newStatus = statusAction.value === 'disable' ? 'disabled' : 'active'

  try {
    await updateUserStatus(currentUser.value.id, {
      status: newStatus,
      reason: statusReason.value
    })

    logger.info(`[AdminUsers] User ${currentUser.value.id} status changed to ${newStatus}`)
    ElMessage.success(`用户已${statusAction.value === 'disable' ? '禁用' : '启用'}`)
    statusDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    logger.error('[AdminUsers] Failed to update user status:', error?.response?.data || error.message)
    ElMessage.error('操作失败')
  }
}

// 导出Excel
async function handleExport() {
  logger.info('[AdminUsers] Exporting users...')

  try {
    const res = await exportUsers(filters)
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `AI小商用户列表_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)

    logger.info('[AdminUsers] Export completed')
    ElMessage.success('导出成功')
  } catch (error) {
    logger.error('[AdminUsers] Export failed:', error?.response?.data || error.message)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  logger.debug('[AdminUsers] Component mounted')
  fetchUsers()
})
</script>

<style scoped>
/* ============================================
   AI小商 管理端用户管理页面
   设计风格: 深色科技风 + 数据表格
   ============================================ */

:root {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --success: #059669;
  --danger: #EF4444;
  --warning: #F59E0B;
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --bg-card-hover: #273549;
  --border-color: #334155;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
}

.admin-users {
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

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group :deep(.el-select) {
  width: 140px;
}

.filter-group :deep(.el-input) {
  width: 220px;
}

.filter-group :deep(.el-input__wrapper) {
  background: var(--bg-dark);
  border-color: var(--border-color);
  box-shadow: none;
}

.filter-group :deep(.el-input__wrapper:hover),
.filter-group :deep(.el-input__wrapper:focus) {
  border-color: var(--primary);
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

.filter-actions :deep(.el-button--primary) {
  background: var(--primary);
  border-color: var(--primary);
}

.filter-actions :deep(.el-button--primary:hover) {
  background: var(--primary-light);
  border-color: var(--primary-light);
}

/* 用户表格 */
.users-table {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.users-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255, 255, 255, 0.02);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.03);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-muted);
}

.users-table :deep(.el-table th) {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.users-table :deep(.el-table td) {
  padding: 16px 12px;
}

/* 用户信息单元格 */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.phone-masked {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--text-secondary);
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.student {
  background: rgba(8, 145, 178, 0.1);
  color: var(--primary-light);
}

.role-badge.teacher {
  background: rgba(139, 92, 246, 0.1);
  color: #A78BFA;
}

.major-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(5, 150, 105, 0.1);
  color: var(--success);
}

.status-badge.disabled {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.time-text {
  font-size: 13px;
  color: var(--text-muted);
}

.chat-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
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

/* 对话框 */
.dialog-content {
  padding: 16px 0;
}

.dialog-content p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px;
}

.dialog-content strong {
  color: var(--text-primary);
}

.reason-input {
  margin-top: 16px;
}

.reason-input label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.reason-input :deep(.el-textarea__inner) {
  background: var(--bg-dark);
  border-color: var(--border-color);
  color: var(--text-primary);
}

:deep(.el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid var(--border-color);
  padding: 16px 24px;
}

:deep(.el-button--danger) {
  background: var(--danger);
  border-color: var(--danger);
}

:deep(.el-button--success) {
  background: var(--success);
  border-color: var(--success);
}
</style>