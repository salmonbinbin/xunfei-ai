<template>
  <div class="profile-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else>
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
        <p class="page-subtitle">管理你的个人信息和设置</p>
      </div>

      <!-- 用户信息卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-large">
            <span>{{ userInitials }}</span>
          </div>
          <div class="user-info">
            <h2>{{ profile.nickname || '未设置昵称' }}</h2>
            <p class="user-id">广州商学院 · {{ profile.major || '未设置专业' }}</p>
          </div>
          <button class="edit-btn" @click="editProfile">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            编辑
          </button>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>手机号</label>
            <span>{{ displayPhone }}</span>
          </div>
          <div class="info-item">
            <label>年级</label>
            <span>{{ profile.grade ? '大' + profile.grade + '年级' : '未设置' }}</span>
          </div>
          <div class="info-item">
            <label>学习目标</label>
            <span>{{ profile.goal || '未设置' }}</span>
          </div>
          <div class="info-item">
            <label>绑定微信</label>
            <span class="wechat-status">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="#07C160">
                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.11.24-.245 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89a4.538 4.538 0 0 0-.407-.032zm-1.562 2.458c.46 0 .833.378.833.844a.838.838 0 0 1-.833.844.838.838 0 0 1-.833-.844c0-.466.373-.844.833-.844zm4.844 0c.46 0 .833.378.833.844a.838.838 0 0 1-.833.844.838.838 0 0 1-.833-.844c0-.466.373-.844.833-.844z"/>
              </svg>
              {{ profile.wechatBound ? '已绑定' : '未绑定' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 数据统计 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(8, 145, 178, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.courses }}</div>
          <div class="stat-label">我的课程</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.reviews }}</div>
          <div class="stat-label">录音回顾</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(2, 132, 199, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.conversations }}</div>
          <div class="stat-label">AI对话</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(168, 85, 247, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.schedules }}</div>
          <div class="stat-label">日程记录</div>
        </div>
      </div>

      <!-- 设置区域 -->
      <div class="settings-section">
        <h3 class="section-title">偏好设置</h3>
        <div class="settings-list">
          <div class="setting-item" @click="toggleVoice">
            <div class="setting-left">
              <div class="setting-icon" style="background: rgba(5, 150, 105, 0.1);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
                </svg>
              </div>
              <div class="setting-text">
                <span>语音播报</span>
                <p>AI回答时自动朗读文字</p>
              </div>
            </div>
            <div :class="['toggle', { active: settings.voiceEnabled }]">
              <div class="toggle-handle"></div>
            </div>
          </div>
          <div class="setting-item" @click="toggleEmotion">
            <div class="setting-left">
              <div class="setting-icon" style="background: rgba(8, 145, 178, 0.1);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
              </div>
              <div class="setting-text">
                <span>情感陪伴模式</span>
                <p>更温暖的对话风格</p>
              </div>
            </div>
            <div :class="['toggle', { active: settings.emotionMode }]">
              <div class="toggle-handle"></div>
            </div>
          </div>
          <div class="setting-item" @click="toggleNotification">
            <div class="setting-left">
              <div class="setting-icon" style="background: rgba(2, 132, 199, 0.1);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </div>
              <div class="setting-text">
                <span>课程提醒</span>
                <p>课前15分钟推送通知</p>
              </div>
            </div>
            <div :class="['toggle', { active: settings.notificationEnabled }]">
              <div class="toggle-handle"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 退出登录 -->
      <div class="actions-section">
        <button class="btn-logout" @click="logout">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          退出登录
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getTodayCourses } from '@/api/timetable'
import { getReviewList } from '@/api/review'
import { getChatConversations } from '@/api/chat'
import { getSchedules } from '@/api/schedule'
import logger from '@/utils/logger'

const router = useRouter()
const userStore = useUserStore()

const profile = ref({
  id: null,
  nickname: '',
  phone: '',
  major: '',
  grade: null,
  goal: '',
  wechatBound: false
})

const stats = ref({
  courses: 0,
  reviews: 0,
  conversations: 0,
  schedules: 0
})

const settings = ref({
  voiceEnabled: true,
  emotionMode: false,
  notificationEnabled: true
})

const loading = ref(true)

const userInitials = computed(() => {
  const name = profile.value.nickname || profile.value.phone || '用户'
  return name.slice(0, 2).toUpperCase()
})

const displayPhone = computed(() => {
  if (!profile.value.phone) return '未绑定'
  const p = profile.value.phone
  return p.slice(0, 3) + '****' + p.slice(-4)
})

onMounted(async () => {
  await loadUserData()
})

async function loadUserData() {
  loading.value = true
  try {
    // 获取当前用户信息
    const userData = await userStore.fetchUser()
    if (userData) {
      profile.value = {
        id: userData.id,
        nickname: userData.nickname || '',
        phone: userData.phone || '',
        major: userData.profile?.major || '',
        grade: userData.profile?.grade || null,
        goal: userData.profile?.goal || '',
        wechatBound: !!userData.openid
      }
    }

    // 并行获取统计数据
    await Promise.all([
      loadCoursesCount(),
      loadReviewsCount(),
      loadConversationsCount(),
      loadSchedulesCount()
    ])
  } catch (error) {
    logger.error('[Profile] Failed to load user data:', error)
  } finally {
    loading.value = false
  }
}

async function loadCoursesCount() {
  try {
    const { data } = await getTodayCourses()
    // API返回的是课程数组
    stats.value.courses = Array.isArray(data) ? data.length : (data.courses?.length || 0)
  } catch (error) {
    logger.error('[Profile] Failed to load courses:', error)
  }
}

async function loadReviewsCount() {
  try {
    const { data } = await getReviewList(100, 0)
    stats.value.reviews = Array.isArray(data) ? data.length : (data.total || 0)
  } catch (error) {
    logger.error('[Profile] Failed to load reviews:', error)
  }
}

async function loadConversationsCount() {
  try {
    const { data } = await getChatConversations()
    // 计算独立会话数
    stats.value.conversations = Array.isArray(data) ? data.length : 0
  } catch (error) {
    logger.error('[Profile] Failed to load conversations:', error)
  }
}

async function loadSchedulesCount() {
  try {
    const { data } = await getSchedules()
    stats.value.schedules = Array.isArray(data) ? data.length : 0
  } catch (error) {
    logger.error('[Profile] Failed to load schedules:', error)
  }
}

function editProfile() {
  alert('编辑资料功能开发中...')
}

function toggleVoice() {
  settings.value.voiceEnabled = !settings.value.voiceEnabled
}

function toggleEmotion() {
  settings.value.emotionMode = !settings.value.emotionMode
}

function toggleNotification() {
  settings.value.notificationEnabled = !settings.value.notificationEnabled
}

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  background: #F8FAFC;
  min-height: 100vh;
}

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

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 15px;
  color: #64748B;
}

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
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E2E8F0;
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

.user-id {
  font-size: 14px;
  color: #64748B;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 10px;
  color: #0891B2;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: rgba(8, 145, 178, 0.12);
  border-color: rgba(8, 145, 178, 0.25);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  color: #94A3B8;
  font-size: 13px;
}

.info-item span {
  color: #475569;
  font-size: 15px;
}

.wechat-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
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
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
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

.settings-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 12px;
  padding-left: 4px;
}

.settings-list {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  overflow: hidden;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.setting-item:not(:last-child) {
  border-bottom: 1px solid #F1F5F9;
}

.setting-item:hover {
  background: #F8FAFC;
}

.setting-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.setting-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.setting-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-text span {
  color: #1E293B;
  font-size: 15px;
  font-weight: 500;
}

.setting-text p {
  color: #94A3B8;
  font-size: 13px;
}

.toggle {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: #E2E8F0;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.toggle.active {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
}

.toggle-handle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.toggle.active .toggle-handle {
  left: 22px;
}

.actions-section {
  margin-top: 32px;
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

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
  .avatar-section {
    flex-wrap: wrap;
  }
  .edit-btn {
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }
}
</style>
