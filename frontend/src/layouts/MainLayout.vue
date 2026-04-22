<template>
  <div class="main-layout min-h-screen bg-page">
    <!-- 简洁顶部导航 -->
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          <div class="brand-icon">
            <svg width="28" height="28" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="url(#navGrad)"/>
              <circle cx="24" cy="18" r="6" fill="white" fill-opacity="0.95"/>
              <path d="M14 34C14 29.5817 18.4183 26 24 26H28C33.5817 26 38 29.5817 38 34V35H14V34Z" fill="white" fill-opacity="0.95"/>
              <defs>
                <linearGradient id="navGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#6366F1"/>
                  <stop offset="1" stop-color="#8B5CF6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="brand-text">AI小商</span>
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
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

// 图标组件
const HomeIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })
    ])
  }
}

const TimetableIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' })
    ])
  }
}

const ChatIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' })
    ])
  }
}

const ReviewIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z' })
    ])
  }
}

const TranslateIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5 12h14M12 5l7 7-7 7' })
    ])
  }
}

const ProfileIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' })
    ])
  }
}

const navItems = [
  { name: '首页', path: '/' },
  { name: '课表', path: '/timetable' },
  { name: 'AI学姐', path: '/ai-sister' },
  { name: '智能翻译', path: '/translate' },
  { name: '录音回顾', path: '/review' },
  { name: '我的', path: '/profile' }
]

const bottomNavItems = [
  { name: '首页', path: '/', icon: HomeIcon },
  { name: '课表', path: '/timetable', icon: TimetableIcon },
  { name: 'AI学姐', path: '/ai-sister', icon: ChatIcon },
  { name: '智能翻译', path: '/translate', icon: TranslateIcon },
  { name: '回顾', path: '/review', icon: ReviewIcon },
  { name: '我的', path: '/profile', icon: ProfileIcon }
]

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* 清新主题变量 */
.main-layout {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --bg-page: #F8FAFC;
  --bg-card: #FFFFFF;
  --text-primary: #1E293B;
  --text-secondary: #64748B;
  --text-muted: #94A3B8;
  --border: #E5E7EB;
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
  filter: drop-shadow(0 2px 4px rgba(99, 102, 241, 0.25));
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
  color: var(--text-primary);
  background: rgba(99, 102, 241, 0.06);
}

.nav-link.active {
  color: var(--primary);
  background: rgba(99, 102, 241, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
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
