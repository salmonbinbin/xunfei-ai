<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">我的</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="pageLoading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else>
      <!-- 个人信心卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-large">
            <span>{{ userInitials }}</span>
          </div>
          <div class="user-info">
            <h2>{{ profile.nickname || '未设置昵称' }}</h2>
            <p class="user-meta">
              广州商学院
              <span v-if="profile.major"> · {{ profile.major }}</span>
              <span v-if="profile.grade"> · 大{{ profile.grade }}年级</span>
            </p>
            <div class="goal-selector-row">
              <span class="goal-label">发展方向：</span>
              <el-select
                v-model="currentGoal"
                placeholder="选择发展方向"
                class="goal-select"
                size="small"
                @change="onGoalChange"
              >
                <el-option
                  v-for="item in goalOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>
          </div>
          <button class="edit-btn" @click="openEditDialog">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            编辑资料
          </button>
        </div>
      </div>

      <!-- 数据统计 3宫格 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(8, 145, 178, 0.1);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.courses }}</div>
          <div class="stat-label">我的课程</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.reviews }}</div>
          <div class="stat-label">录音回顾</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(168, 85, 247, 0.1);">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.conversations }}</div>
          <div class="stat-label">AI对话</div>
        </div>
      </div>

      <!-- 最近活动时间线 -->
      <div class="timeline-card">
        <div class="timeline-header">
          <span class="timeline-title">最近活动</span>
        </div>
        <div v-if="recentActivities.length === 0" class="timeline-empty">
          <p>暂无最近活动</p>
          <p class="empty-hint">开始使用AI小商，开启你的智慧校园生活吧</p>
        </div>
        <div v-else class="timeline-list">
          <div
            v-for="(activity, index) in recentActivities"
            :key="index"
            class="timeline-item"
            @click="onActivityClick(activity)"
          >
            <div class="timeline-icon-wrap">
              <span class="timeline-icon">{{ activity.icon }}</span>
              <span v-if="index < recentActivities.length - 1" class="timeline-line"></span>
            </div>
            <div class="timeline-content">
              <div class="timeline-time">{{ activity.relativeTime }}</div>
              <div class="timeline-item-title">{{ activity.title }}</div>
              <div class="timeline-item-sub">{{ activity.subtitle }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 退出登录 -->
      <div class="actions-section">
        <button class="btn-logout" @click="showLogoutDialog = true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          退出登录
        </button>
      </div>
    </template>

    <!-- 编辑资料弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑资料"
      width="480px"
      :close-on-click-modal="false"
      class="edit-profile-dialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-position="top"
      >
        <el-form-item label="昵称" prop="nickname">
          <el-input
            v-model="editForm.nickname"
            placeholder="请输入昵称"
            maxlength="20"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="专业" prop="major">
          <el-input
            v-model="editForm.major"
            placeholder="请输入专业"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select v-model="editForm.grade" placeholder="请选择年级" style="width: 100%;">
            <el-option :value="1" label="大一年级" />
            <el-option :value="2" label="大二年级" />
            <el-option :value="3" label="大三年级" />
            <el-option :value="4" label="大四年级" />
          </el-select>
        </el-form-item>
        <el-form-item label="发展方向" prop="goal">
          <el-select v-model="editForm.goal" placeholder="请选择发展方向" style="width: 100%;">
            <el-option
              v-for="item in goalOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSaveProfile">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 退出登录确认 -->
    <el-dialog
      v-model="showLogoutDialog"
      title="退出登录"
      width="400px"
      class="logout-dialog"
    >
      <p>确定要退出登录吗？</p>
      <template #footer>
        <el-button @click="showLogoutDialog = false">取消</el-button>
        <el-button type="danger" :loading="logoutLoading" @click="handleLogout">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getReviewList } from '@/api/review'
import { getConversations } from '@/api/chat'
import { getCourses } from '@/api/timetable'
import logger from '@/utils/logger'

const router = useRouter()
const userStore = useUserStore()

// 发展方向选项
const goalOptions = [
  { value: '考研', label: '考研' },
  { value: '考公', label: '考公' },
  { value: '就业', label: '就业' },
  { value: '出国', label: '出国' },
  { value: '未定', label: '未定' }
]

// 页面状态
const pageLoading = ref(true)
const saveLoading = ref(false)
const logoutLoading = ref(false)
const editDialogVisible = ref(false)
const showLogoutDialog = ref(false)
const editFormRef = ref(null)

// 用户信息
const profile = ref({
  nickname: '',
  major: '',
  grade: null,
  goal: null
})

// 发展方向本地副本（用于即时显示）
const currentGoal = ref('')

// 数据统计
const stats = ref({
  courses: 0,
  reviews: 0,
  conversations: 0,
  schedules: 0
})

// 最近活动时间线
const recentActivities = ref([])

// 编辑表单
const editForm = ref({
  nickname: '',
  major: '',
  grade: null,
  goal: ''
})

// 表单验证规则
const editFormRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { max: 20, message: '昵称最多20个字符', trigger: 'blur' }
  ],
  major: [
    { max: 100, message: '专业最多100个字符', trigger: 'blur' }
  ],
  grade: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  goal: [
    { required: true, message: '请选择发展方向', trigger: 'change' }
  ]
}

// 计算属性
const userInitials = computed(() => {
  const name = profile.value.nickname || '用户'
  return name.slice(0, 2).toUpperCase()
})

// 相对时间格式化
function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  const monthDay = `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  return monthDay
}

// 加载用户数据
async function loadUserData() {
  pageLoading.value = true
  try {
    const userData = await userStore.fetchUser()
    if (userData) {
      profile.value = {
        nickname: userData.nickname || '',
        major: userData.profile?.major || '',
        grade: userData.profile?.grade || null,
        goal: userData.profile?.goal || ''
      }
      currentGoal.value = profile.value.goal || ''
      logger.info('[Profile] User data loaded', {
        id: userData.id,
        hasProfile: userData.has_profile
      })
    }

    await Promise.all([
      loadStats(),
      loadRecentActivities()
    ])
  } catch (error) {
    logger.error('[Profile] Failed to load user data:', error)
  } finally {
    pageLoading.value = false
  }
}

// 加载统计数据
async function loadStats() {
  try {
    const [reviewRes, chatRes, courseRes] = await Promise.all([
      getReviewList({ limit: 100, skip: 0 }).catch(() => ({ data: [] })),
      getConversations().catch(() => ({ data: [] })),
      getCourses().catch(() => ({ data: [] }))
    ])

    stats.value.reviews = Array.isArray(reviewRes.data) ? reviewRes.data.length : 0
    stats.value.conversations = Array.isArray(chatRes.data) ? chatRes.data.length : 0
    stats.value.courses = Array.isArray(courseRes.data) ? courseRes.data.length : 0

    logger.debug('[Profile] Stats loaded', { stats: stats.value })
  } catch (error) {
    logger.error('[Profile] Failed to load stats:', error)
  }
}

// 加载最近活动时间线
async function loadRecentActivities() {
  try {
    const [reviewRes, chatRes] = await Promise.all([
      getReviewList({ status: 'completed', limit: 3, skip: 0 }).catch(() => ({ data: [] })),
      getConversations().catch(() => ({ data: [] }))
    ])

    const activities = []

    // 录音回顾
    if (Array.isArray(reviewRes.data)) {
      reviewRes.data.slice(0, 3).forEach(item => {
        activities.push({
          type: 'review',
          icon: '🎙️',
          title: item.title || '录音回顾',
          subtitle: item.record_type === 'course' ? '课程录音' : '会议录音',
          time: item.updated_at || item.created_at,
          relativeTime: formatRelativeTime(item.updated_at || item.created_at),
          id: item.id,
          url: `/review/${item.id}`
        })
      })
    }

    // AI对话
    if (Array.isArray(chatRes.data)) {
      chatRes.data.slice(0, 3).forEach(item => {
        activities.push({
          type: 'chat',
          icon: '💬',
          title: item.title || 'AI对话',
          subtitle: `${item.message_count || 0}条消息`,
          time: item.updated_at || item.created_at,
          relativeTime: formatRelativeTime(item.updated_at || item.created_at),
          id: item.id,
          url: `/ai-sister?conv=${item.id}`
        })
      })
    }

    // 按时间倒序排序
    activities.sort((a, b) => new Date(b.time) - new Date(a.time))
    recentActivities.value = activities.slice(0, 5)

    logger.debug('[Profile] Recent activities loaded', { count: recentActivities.value.length })
  } catch (error) {
    logger.error('[Profile] Failed to load recent activities:', error)
  }
}

// 发展方向变更（自动保存）
async function onGoalChange(newGoal) {
  logger.info('[Profile] Goal changing', { from: profile.value.goal, to: newGoal })
  try {
    await userStore.updateProfile({ goal: newGoal })
    profile.value.goal = newGoal
    ElMessage.success('发展方向已更新')
    logger.info('[Profile] Goal updated successfully', { goal: newGoal })
  } catch (error) {
    // 失败后回滚选择
    currentGoal.value = profile.value.goal
    logger.error('[Profile] Goal update failed:', error)
  }
}

// 打开编辑弹窗
function openEditDialog() {
  editForm.value = {
    nickname: profile.value.nickname,
    major: profile.value.major,
    grade: profile.value.grade,
    goal: profile.value.goal
  }
  editDialogVisible.value = true
  logger.debug('[Profile] Edit dialog opened', { form: editForm.value })
}

// 保存资料
async function handleSaveProfile() {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    saveLoading.value = true
    try {
      logger.info('[Profile] Saving profile', { data: editForm.value })
      await userStore.updateProfile(editForm.value)

      profile.value = {
        nickname: editForm.value.nickname,
        major: editForm.value.major,
        grade: editForm.value.grade,
        goal: editForm.value.goal
      }
      currentGoal.value = editForm.value.goal

      editDialogVisible.value = false
      ElMessage.success('资料完善成功')
      logger.info('[Profile] Profile saved successfully')

      await loadStats()
    } catch (error) {
      logger.error('[Profile] Profile save failed:', error)
    } finally {
      saveLoading.value = false
    }
  })
}

// 活动点击
function onActivityClick(activity) {
  logger.debug('[Profile] Activity clicked', { type: activity.type, id: activity.id })
  if (activity.url) {
    router.push(activity.url)
  }
}

// 退出登录
async function handleLogout() {
  logoutLoading.value = true
  try {
    logger.info('[Profile] User logging out')
    userStore.logout()
    showLogoutDialog.value = false
    router.push('/login')
  } catch (error) {
    logger.error('[Profile] Logout failed:', error)
  } finally {
    logoutLoading.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.profile-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  background: #F8FAFC;
  min-height: 100vh;
  padding-bottom: 100px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.loading-state .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(8, 145, 178, 0.2);
  border-top-color: #0891B2;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-state p {
  color: #64748B;
  font-size: 14px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 个人信心卡片 */
.profile-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.avatar-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.avatar-large {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.user-meta {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 8px;
}

.goal-selector-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.goal-label {
  font-size: 14px;
  color: #64748B;
}

.goal-select {
  width: 120px;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 12px;
  color: #0891B2;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.edit-btn:hover {
  background: rgba(8, 145, 178, 0.12);
  border-color: rgba(8, 145, 178, 0.25);
}

/* 数据统计3宫格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px 12px;
  text-align: center;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #0891B2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.stat-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #64748B;
}

/* 时间线 */
.timeline-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.timeline-header {
  margin-bottom: 20px;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.timeline-empty {
  text-align: center;
  padding: 32px 0;
  color: #64748B;
}

.timeline-empty p {
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: #94A3B8;
}

.timeline-list {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 12px;
  cursor: pointer;
  padding: 8px 0;
  transition: background 0.2s ease;
  border-radius: 8px;
}

.timeline-item:hover {
  background: #F8FAFC;
}

.timeline-icon-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timeline-icon {
  font-size: 18px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F8FAFC;
  border-radius: 50%;
}

.timeline-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: #E2E8F0;
  margin-top: 6px;
}

.timeline-content {
  flex: 1;
  padding-bottom: 8px;
}

.timeline-time {
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 2px;
}

.timeline-item-title {
  font-size: 15px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 2px;
}

.timeline-item-sub {
  font-size: 13px;
  color: #94A3B8;
}

/* 退出登录 */
.actions-section {
  margin-top: 8px;
}

.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 12px;
  color: #EF4444;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.25);
}

/* Element Plus 弹窗样式覆盖 */
:deep(.el-dialog) {
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #F1F5F9;
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
  border-top: 1px solid #F1F5F9;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #475569;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 10px;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .avatar-section {
    flex-wrap: wrap;
  }
  .edit-btn {
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }
  .goal-selector-row {
    flex-wrap: wrap;
  }
}
</style>
