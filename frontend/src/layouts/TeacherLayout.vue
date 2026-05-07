<template>
  <div class="teacher-layout">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/teacher" class="nav-brand">
          <div class="brand-icon">
            <svg width="28" height="28" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="url(#teacherGrad)"/>
              <circle cx="24" cy="18" r="6" fill="white" fill-opacity="0.95"/>
              <circle cx="21.5" cy="17" r="1.5" fill="#0891B2"/>
              <circle cx="26.5" cy="17" r="1.5" fill="#0891B2"/>
              <path d="M21 21C21 21 22.5 23 24 23C25.5 23 27 21 27 21" stroke="#0891B2" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M14 34C14 29.5817 18.4183 26 24 26H28C33.5817 26 38 29.5817 38 34V35H14V34Z" fill="white" fill-opacity="0.95"/>
              <defs>
                <linearGradient id="teacherGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#0891B2"/>
                  <stop offset="1" stop-color="#22D3EE"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="brand-text">AI小商教师端</span>
        </router-link>

        <div class="nav-links">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActive(item.path) }"
          >
            {{ item.name }}
          </router-link>
        </div>

        <div class="nav-actions">
          <div class="user-info">
            <span class="user-name">{{ userStore.userInfo?.name || '教师' }}</span>
          </div>
          <button @click="handleLogout" class="logout-btn" title="退出登录">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 底部导航（移动端） -->
    <nav class="bottom-nav">
      <router-link
        v-for="item in bottomNavItems"
        :key="item.path"
        :to="item.path"
        class="bottom-nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <component :is="item.icon" class="nav-icon" />
        <span class="nav-label">{{ item.name }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

// 图标组件
const GradeIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
    ])
  }
}

const NotificationIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
    ])
  }
}

const LessonPlanIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ])
  }
}

const HomeIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
    ])
  }
}

// 导航项
const navItems = [
  { name: '首页', path: '/teacher' },
  { name: '成绩管理', path: '/teacher/grade' },
  { name: '通知发布', path: '/teacher/notification' },
  { name: '备课教案', path: '/teacher/lesson-plan' },
  { name: '我的', path: '/teacher/profile' }
]

// 底部导航项（移动端）
const bottomNavItems = [
  { name: '首页', path: '/teacher', icon: HomeIcon },
  { name: '成绩', path: '/teacher/grade', icon: GradeIcon },
  { name: '通知', path: '/teacher/notification', icon: NotificationIcon },
  { name: '教案', path: '/teacher/lesson-plan', icon: LessonPlanIcon }
]

function handleLogout() {
  userStore.logout()
  router.push('/teacher/login')
}
</script>

<style scoped>
.teacher-layout {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --bg-page: #F8FAFC;
  --bg-card: #FFFFFF;
  --text-primary: #1E293B;
  --text-secondary: #64748B;
  --text-muted: #94A3B8;
  --border: #E2E8F0;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 顶部导航 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.brand-icon {
  filter: drop-shadow(0 2px 4px rgba(8, 145, 178, 0.25));
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 1px;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--primary);
  background: rgba(8, 145, 178, 0.06);
}

.nav-link.active {
  color: var(--primary);
  background: rgba(8, 145, 178, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(8, 145, 178, 0.06);
  border-radius: 8px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--primary);
}

.logout-btn {
  padding: 8px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn:hover {
  color: #EF4444;
  background: rgba(239, 68, 68, 0.08);
}

/* 主内容区 */
.main-content {
  padding-top: 80px;
  padding-bottom: 100px;
  max-width: 100%;
}

/* 底部导航 */
.bottom-nav {
  display: none;
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .navbar {
    height: 56px;
  }

  .nav-container {
    padding: 0 16px;
  }

  .brand-text {
    font-size: 16px;
  }

  .user-info {
    display: none;
  }

  .bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 72px;
    background: var(--bg-card);
    border-top: 1px solid var(--border);
    padding-bottom: env(safe-area-inset-bottom);
    z-index: 100;
  }

  .bottom-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    text-decoration: none;
    color: var(--text-muted);
    transition: all 0.2s ease;
  }

  .bottom-nav-item.active {
    color: var(--primary);
  }

  .nav-icon {
    width: 24px;
    height: 24px;
  }

  .nav-label {
    font-size: 11px;
    font-weight: 500;
  }

  .main-content {
    padding-top: 64px;
    padding-bottom: 90px;
  }
}
</style>