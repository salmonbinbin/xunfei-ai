<template>
  <div class="users-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          用户管理
        </h1>
        <p class="page-desc">共 {{ pagination.total }} 位用户</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleRefresh">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          刷新
        </el-button>
        <el-button @click="handleExport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出
        </el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label>角色</label>
          <el-select v-model="filters.role" placeholder="全部" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </div>
        <div class="filter-item">
          <label>状态</label>
          <el-select v-model="filters.status" placeholder="全部" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="正常" value="active" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </div>
        <div class="filter-item search">
          <label>搜索</label>
          <el-input
            v-model="filters.keyword"
            placeholder="昵称 / 手机号"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </template>
          </el-input>
        </div>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-card">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="nickname" label="用户信息" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="avatar" :class="row.role">{{ row.nickname?.[0] || 'U' }}</div>
              <div class="info">
                <div class="name">{{ row.nickname || '未设置' }}</div>
                <div class="phone">{{ row.phone }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <span class="role-tag" :class="row.role">
              {{ row.role === 'student' ? '学生' : '教师' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="专业/院系" min-width="140">
          <template #default="{ row }">
            <span class="meta">{{ row.role === 'teacher' ? (row.department || '-') : (row.major || '-') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'active'" type="success" size="small">正常</el-tag>
            <el-popover v-else placement="top" :width="220" trigger="hover">
              <template #reference>
                <el-tag type="danger" size="small" class="disabled-tag">
                  <span class="dot"></span>已禁用
                </el-tag>
              </template>
              <div class="reason-popover">
                <div class="reason-title">禁用原因</div>
                <div class="reason-content">{{ row.disable_reason || '未说明' }}</div>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="140">
          <template #default="{ row }">
            <span class="time">{{ row.last_login ? formatTime(row.last_login) : '从未登录' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button
              :type="row.status === 'active' ? 'warning' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-area">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 状态切换对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      :title="statusAction === 'disable' ? '禁用用户' : '启用用户'"
      width="420px"
      align-center
      :show-close="false"
    >
      <div class="dialog-body">
        <div class="dialog-user" v-if="currentUser">
          <div class="dialog-avatar" :class="currentUser.role">{{ currentUser.nickname?.[0] }}</div>
          <div class="dialog-info">
            <div class="dialog-name">{{ currentUser.nickname }}</div>
            <div class="dialog-phone">{{ currentUser.phone }}</div>
          </div>
        </div>
        <div class="dialog-message">
          确定要{{ statusAction === 'disable' ? '禁用' : '启用' }}该用户吗？
        </div>
        <div class="reason-field" v-if="statusAction === 'disable'">
          <label>禁用原因 <span class="optional">(将告知用户)</span></label>
          <el-input
            v-model="statusReason"
            type="textarea"
            :rows="3"
            placeholder="请输入禁用原因..."
            maxlength="200"
            show-word-limit
          />
        </div>
        <div class="warning-hint" v-if="statusAction === 'disable' && !statusReason">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>建议填写原因，用户可见</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button :type="statusAction === 'disable' ? 'warning' : 'success'" @click="confirmStatusChange">
          确认{{ statusAction === 'disable' ? '禁用' : '启用' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, updateUserStatus, exportUsers } from '@/api/admin/user'
import logger from '@/utils/logger'

const users = ref([])
const loading = ref(false)

const filters = reactive({
  role: '',
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const statusDialogVisible = ref(false)
const statusAction = ref('disable')
const currentUser = ref(null)
const statusReason = ref('')

async function fetchUsers() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, ...filters }
    const res = await getUsers(params)
    const data = res.data?.data || res.data || {}
    users.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    logger.error('[AdminUsers] Failed to fetch users:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  pagination.page = 1
  fetchUsers()
}

function handleSearch() {
  pagination.page = 1
  fetchUsers()
}

function handleRefresh() {
  fetchUsers()
}

function handlePageChange(page) {
  pagination.page = page
  fetchUsers()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchUsers()
}

function handleToggleStatus(user) {
  currentUser.value = user
  statusAction.value = user.status === 'active' ? 'disable' : 'enable'
  statusReason.value = ''
  statusDialogVisible.value = true
}

async function confirmStatusChange() {
  if (!currentUser.value) return
  const newStatus = statusAction.value === 'disable' ? 'disabled' : 'active'
  try {
    await updateUserStatus(currentUser.value.id, {
      status: newStatus,
      reason: statusReason.value
    })
    ElMessage.success(`用户已${statusAction.value === 'disable' ? '禁用' : '启用'}`)
    statusDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    logger.error('[AdminUsers] Failed to update status:', error)
    ElMessage.error('操作失败')
  }
}

async function handleExport() {
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
    ElMessage.success('导出成功')
  } catch (error) {
    logger.error('[AdminUsers] Export failed:', error)
    ElMessage.error('导出失败')
  }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return `${d.getMonth()+1}/${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
}

/* 页面标题区 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.page-title svg {
  width: 28px;
  height: 28px;
  color: #0891B2;
}

.page-desc {
  font-size: 14px;
  color: #64748B;
  margin: 0;
  padding-left: 40px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-actions :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 14px;
}

.header-actions :deep(.el-button svg) {
  width: 16px;
  height: 16px;
}

/* 筛选区 */
.filter-section {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.filter-item.search {
  flex: 1;
  min-width: 200px;
}

.filter-item :deep(.el-select) {
  width: 120px;
}

.filter-item.search :deep(.el-input) {
  width: 100%;
}

/* 用户卡片 */
.users-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow-x: auto;
}

.users-card :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #F8FAFC;
  --el-table-row-hover-bg-color: #F1F5F9;
  --el-table-border-color: #E2E8F0;
  --el-table-text-color: #1E293B;
  --el-table-header-text-color: #475569;
}

.users-card :deep(.el-table th) {
  font-weight: 600;
  font-size: 13px;
  padding: 14px 12px;
}

.users-card :deep(.el-table td) {
  padding: 14px 12px;
  font-size: 14px;
}

/* 表格单元格 - 强制文字横向显示 */
.users-card :deep(.el-table .cell) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  white-space: normal !important;
}

.users-card :deep(.el-table td) {
  vertical-align: middle !important;
}

.users-card :deep(.el-table .el-table__row) {
  height: 60px;
}

/* 用户单元格 */
.user-cell {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 12px;
  flex: 1;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.avatar.student {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
}

.avatar.teacher {
  background: linear-gradient(135deg, #8B5CF6, #A78BFA);
}

.info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.name {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.phone {
  font-size: 13px;
  color: #64748B;
  font-family: 'JetBrains Mono', monospace;
}

/* 角色标签 */
.role-tag {
  display: inline-flex !important;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.role-tag.student {
  background: rgba(8, 145, 178, 0.1);
  color: #0891B2;
}

.role-tag.teacher {
  background: rgba(139, 92, 246, 0.1);
  color: #7C3AED;
}

/* 专业/院系 */
.meta {
  font-size: 14px;
  color: #475569;
  white-space: nowrap;
}

/* 禁用标签 */
.disabled-tag {
  cursor: pointer;
}

.disabled-tag .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  margin-right: 4px;
}

/* 禁用原因弹出 */
.reason-popover {
  padding: 4px 0;
}

.reason-title {
  font-size: 12px;
  color: #64748B;
  margin-bottom: 6px;
}

.reason-content {
  font-size: 14px;
  color: #1E293B;
  line-height: 1.5;
}

/* 时间 */
.time {
  font-size: 13px;
  color: #64748B;
  white-space: nowrap;
}

/* 对话次数 */
.count {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

/* 分页 */
.pagination-area {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #E2E8F0;
}

.pagination-area :deep(.el-pagination) {
  font-weight: 400;
}

/* 对话框 */
.dialog-body {
  padding: 8px 0;
}

.dialog-user {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 10px;
  margin-bottom: 16px;
}

.dialog-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.dialog-avatar.student {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
}

.dialog-avatar.teacher {
  background: linear-gradient(135deg, #8B5CF6, #A78BFA);
}

.dialog-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dialog-name {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.dialog-phone {
  font-size: 14px;
  color: #64748B;
}

.dialog-message {
  font-size: 15px;
  color: #475569;
  margin-bottom: 16px;
}

.reason-field {
  margin-bottom: 12px;
}

.reason-field label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 8px;
}

.reason-field .optional {
  font-size: 12px;
  font-weight: 400;
  color: #94A3B8;
}

.warning-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #FEF3C7;
  border-radius: 8px;
  font-size: 13px;
  color: #92400E;
}

.warning-hint svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

:deep(.el-dialog) {
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
  margin-right: 0;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #E2E8F0;
}

:deep(.el-tag--small) {
  padding: 0 8px;
  height: 24px;
  line-height: 22px;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
  .users-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .page-desc {
    padding-left: 40px;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    width: 100%;
  }

  .filter-item :deep(.el-select),
  .filter-item.search :deep(.el-input) {
    width: 100%;
  }

  .users-card :deep(.el-table) {
    font-size: 13px;
  }

  .users-card :deep(.el-table td) {
    padding: 10px 8px;
  }

  .users-card :deep(.el-table th) {
    padding: 12px 8px;
    font-size: 12px;
  }

  .avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .name {
    font-size: 13px;
  }

  .phone {
    font-size: 12px;
  }

  .role-tag {
    padding: 2px 8px;
    font-size: 11px;
  }

  .meta {
    font-size: 13px;
  }

  .time {
    font-size: 12px;
  }

  .pagination-area {
    padding: 12px;
  }

  .pagination-area :deep(.el-pagination) {
    font-size: 12px;
  }
}
</style>
