<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <h2 class="user-name">{{ userStore.userInfo?.name || '教师' }}</h2>
        <p class="user-role">教师账号</p>
      </div>
    </div>

    <div class="profile-content">
      <div class="info-card">
        <div class="info-item">
          <div class="info-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
          </div>
          <div class="info-content">
            <span class="info-label">手机号</span>
            <span class="info-value">{{ userStore.userInfo?.phone || '-' }}</span>
          </div>
        </div>

        <div class="info-item">
          <div class="info-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div class="info-content">
            <span class="info-label">院系</span>
            <span class="info-value">{{ userStore.userInfo?.department || '-' }}</span>
          </div>
        </div>

        <div class="info-item">
          <div class="info-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <div class="info-content">
            <span class="info-label">职称</span>
            <span class="info-value">{{ userStore.userInfo?.title || '-' }}</span>
          </div>
        </div>
      </div>

      <div class="actions-card">
        <button class="logout-btn" @click="handleLogout">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

function handleLogout() {
  userStore.logout()
  router.push('/teacher/login')
}
</script>

<style scoped>
.profile-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
}

.profile-header {
  background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%);
  border-radius: 20px;
  padding: 32px 24px;
  margin-bottom: 24px;
  text-align: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.user-name {
  font-size: 24px;
  font-weight: 600;
  color: white;
  margin: 0 0 4px;
}

.user-role {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #F1F5F9;
}

.info-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-item:first-child {
  padding-top: 0;
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(8, 145, 178, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 13px;
  color: #94A3B8;
}

.info-value {
  font-size: 15px;
  color: #1E293B;
  font-weight: 500;
}

.actions-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 12px;
  color: #EF4444;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #FEE2E2;
  border-color: #FCA5A5;
}
</style>