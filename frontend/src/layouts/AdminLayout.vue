<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <header class="admin-header">
      <div class="header-left">
        <router-link to="/admin/dashboard" class="logo-link">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="logo-text">
            <span class="logo-title">AI小商</span>
            <span class="logo-subtitle">运营平台</span>
          </div>
        </router-link>
      </div>

      <nav class="header-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'active': isActive(item.path) }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="header-right">
        <div class="time-display">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{{ currentTime }}</span>
        </div>

        <el-dropdown @command="handleCommand" trigger="click">
          <div class="admin-profile">
            <div class="admin-avatar">
              {{ adminStore.adminInfo?.nickname?.[0] || 'A' }}
            </div>
            <span class="admin-name">{{ adminStore.adminInfo?.nickname || '管理员' }}</span>
            <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout" divided>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="admin-main">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 侧边栏折叠按钮 -->
    <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline :points="sidebarCollapsed ? '9 18 15 12 9 6' : '15 18 9 12 15 6'"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import logger from '@/utils/logger'

const router = useRouter()
const route = useRoute()
const adminStore = useAdminStore()

const sidebarCollapsed = ref(false)
const currentTime = ref('')
let timeInterval = null

// 导航项
const navItems = [
  {
    path: '/admin/dashboard',
    label: '数据驾驶舱',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('rect', { x: '3', y: '3', width: '7', height: '7' }),
        h('rect', { x: '14', y: '3', width: '7', height: '7' }),
        h('rect', { x: '14', y: '14', width: '7', height: '7' }),
        h('rect', { x: '3', y: '14', width: '7', height: '7' })
      ])
    }
  },
  {
    path: '/admin/users',
    label: '用户管理',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
        h('circle', { cx: '9', cy: '7', r: '4' }),
        h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
        h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
      ])
    }
  },
  {
    path: '/admin/logs',
    label: '操作日志',
    icon: {
      render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
        h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
        h('polyline', { points: '14 2 14 8 20 8' }),
        h('line', { x1: '16', y1: '13', x2: '8', y2: '13' }),
        h('line', { x1: '16', y1: '17', x2: '8', y2: '17' }),
        h('polyline', { points: '10 9 9 9 8 9' })
      ])
    }
  }
]

// 判断导航是否激活
function isActive(path) {
  return route.path.startsWith(path)
}

// 更新时间
function updateTime() {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}:${seconds}`
}

// 处理下拉菜单命令
async function handleCommand(command) {
  logger.info('[AdminLayout] Dropdown command:', command)
  if (command === 'logout') {
    await adminStore.logout()
    logger.info('[AdminLayout] Redirecting to login page')
    router.push('/admin/login')
  }
}

onMounted(() => {
  logger.debug('[AdminLayout] Component mounted')
  adminStore.fetchProfile()
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
/* ============================================
   AI小商 管理端布局组件
   设计风格: 深色科技风 + 玻璃拟态
   ============================================ */

:root {
  --primary: #0891B2;
  --primary-light: #22D3EE;
  --bg-dark: #0F172A;
  --bg-card: #1E293B;
  --bg-card-hover: #273549;
  --border-color: #334155;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --success: #059669;
  --danger: #EF4444;
}

.admin-layout {
  min-height: 100vh;
  background: var(--bg-dark);
  font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
}

/* 顶部导航栏 */
.admin-header {
  height: 72px;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* Logo */
.header-left {
  flex: 0 0 auto;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(8, 145, 178, 0.3);
}

.logo-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 3px;
}

/* 导航 */
.header-nav {
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0 40px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.25s ease;
  position: relative;
}

.nav-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  color: var(--primary-light);
  background: rgba(8, 145, 178, 0.1);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
  border-radius: 2px;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

/* 右侧信息 */
.header-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-secondary);
}

.time-display svg {
  width: 14px;
  height: 14px;
  opacity: 0.7;
}

.admin-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.admin-profile:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.admin-avatar {
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

.admin-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.admin-profile:hover .dropdown-arrow {
  color: var(--text-secondary);
}

/* 主内容区域 */
.admin-main {
  padding: 32px;
  margin-top: 72px;
  min-height: calc(100vh - 72px);
}

/* 路由切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 侧边栏切换按钮 */
.sidebar-toggle {
  position: fixed;
  left: 16px;
  bottom: 24px;
  width: 44px;
  height: 44px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 999;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.sidebar-toggle:hover {
  background: var(--bg-card-hover);
  border-color: var(--primary);
}

.sidebar-toggle svg {
  width: 18px;
  height: 18px;
  color: var(--text-secondary);
  transition: transform 0.3s;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

:deep(.el-dropdown-menu__item--divided) {
  margin-top: 4px;
  border-top: 1px solid var(--border-color);
  padding-top: 14px;
}

:deep(.el-dropdown-menu__item svg) {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}
</style>