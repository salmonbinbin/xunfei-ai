<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <div class="top-bar">
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 14l9-5-9-5-9 5 9 5z"/>
            <path d="M12 14l6.16-3.42a12.08 12.08 0 01.65 6.42l-6.81 4 6.16 3.42L12 21l-6.16-3.42L5.03 17l6.81-4-.65 6.42L12 14z"/>
          </svg>
        </div>
        <span class="brand-name">AI小商</span>
      </div>
      <div class="user-chip">
        <div class="user-avatar">{{ userAvatarText }}</div>
        <span class="user-name">{{ userDisplayName }}</span>
      </div>
    </div>

    <!-- 今日课程大卡片 -->
    <div class="today-hero">
      <div class="today-header">
        <div>
          <div class="today-label">今日课程</div>
          <div class="today-date">{{ currentDateText }}</div>
        </div>
        <div class="today-count" v-if="todayCourses.length > 0">
          <div class="count-number">{{ todayCourses.length }}</div>
          <div class="count-label">节课</div>
        </div>
      </div>
      <div class="today-courses" v-if="todayCourses.length > 0">
        <div class="course-chip" v-for="course in todayCourses" :key="course.id">
          <div class="course-chip-time">{{ course.start_time }} · {{ course.start_slot }}-{{ course.end_slot }}节</div>
          <div class="course-chip-name">{{ course.name }}</div>
          <div class="course-chip-location">{{ course.location || '未指定地点' }}</div>
        </div>
      </div>
      <div class="no-course" v-else>
        <div class="no-course-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <p>今天没有课程安排</p>
        <router-link to="/timetable/import" class="import-link">导入课表</router-link>
      </div>
    </div>

    <!-- 快捷服务 -->
    <div class="quick-section">
      <h2 class="section-title">快捷服务</h2>
      <div class="quick-grid">
        <router-link to="/timetable" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="quick-name">课表管理</div>
          <div class="quick-desc">查看和导入</div>
        </router-link>

        <router-link to="/ai-sister" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
          </div>
          <div class="quick-name">AI学姐</div>
          <div class="quick-desc">智能对话</div>
        </router-link>

        <router-link to="/review" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
              <path d="M19 10v2a7 7 0 01-14 0v-2"/>
            </svg>
          </div>
          <div class="quick-name">录音回顾</div>
          <div class="quick-desc">转写总结</div>
        </router-link>

        <router-link to="/course-advisor" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="quick-name">选课助手</div>
          <div class="quick-desc">智能推荐</div>
        </router-link>

        <router-link to="/translate" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="quick-name">智能翻译</div>
          <div class="quick-desc">文档导出</div>
        </router-link>

        <router-link to="/activity" class="quick-item">
          <div class="quick-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
          </div>
          <div class="quick-name">活动助手</div>
          <div class="quick-desc">策划文案</div>
        </router-link>
      </div>
    </div>

    <!-- AI学姐 -->
    <div class="ai-section">
      <div class="ai-avatar">AI</div>
      <div class="ai-content">
        <div class="ai-title">有问题？问问AI学姐</div>
        <div class="ai-desc">可以帮你查课表、问选课、了解校园信息...</div>
      </div>
      <router-link to="/ai-sister" class="ai-action">开始对话</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useTimetableStore } from '@/stores/timetable'

const userStore = useUserStore()
const timetableStore = useTimetableStore()

// 计算用户头像文字
const userAvatarText = computed(() => {
  const name = userStore.userInfo?.nickname
  if (!name) return '同'
  return name.slice(0, 1)
})

// 用户名显示
const userDisplayName = computed(() => {
  const name = userStore.userInfo?.nickname
  if (!name) return '同学'
  return `${name}同学`
})

// 今日课程
const todayCourses = computed(() => timetableStore.todayCourses)

// 当前日期文本
const currentDateText = computed(() => {
  const now = new Date()
  const month = now.getMonth() + 1
  const day = now.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekday = weekdays[now.getDay()]
  return `${month}月${day}日 ${weekday}`
})

onMounted(async () => {
  // 确保用户信息已加载
  if (!userStore.userInfo) {
    await userStore.fetchUser()
  }
  // 获取今日课程数据
  await timetableStore.fetchTodayData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #F8FAFC;
  padding: 24px 24px 100px;
}

/* 顶部导航条 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  font-weight: 600;
}

.user-name {
  font-size: 13px;
  color: #64748B;
}

/* 今日课程 - 全宽大卡片 */
.today-hero {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border-radius: 24px;
  padding: 28px 32px;
  color: white;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}

.today-hero::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.today-hero::after {
  content: '';
  position: absolute;
  bottom: -30px;
  right: 100px;
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
}

.today-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.today-label {
  font-size: 13px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.today-date {
  font-size: 22px;
  font-weight: 700;
}

.today-count {
  text-align: right;
}

.count-number {
  font-size: 36px;
  font-weight: 700;
}

.count-label {
  font-size: 12px;
  opacity: 0.8;
}

.today-courses {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  position: relative;
  z-index: 1;
}

.course-chip {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  flex-shrink: 0;
  min-width: 140px;
}

.course-chip-time {
  font-size: 11px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.course-chip-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.course-chip-location {
  font-size: 11px;
  opacity: 0.7;
}

/* 无课程状态 */
.no-course {
  text-align: center;
  padding: 20px 0;
  position: relative;
  z-index: 1;
}

.no-course-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-course-icon svg {
  width: 24px;
  height: 24px;
  opacity: 0.8;
}

.no-course p {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.import-link {
  font-size: 13px;
  color: white;
  opacity: 0.9;
  text-decoration: none;
}

.import-link:hover {
  opacity: 1;
  text-decoration: underline;
}

/* 快捷服务 */
.quick-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 14px;
  color: #64748B;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quick-item {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  text-decoration: none;
}

.quick-item:hover {
  border-color: #0891B2;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 145, 178, 0.12);
}

.quick-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-icon svg {
  width: 22px;
  height: 22px;
}

.quick-item:nth-child(1) .quick-icon { background: rgba(8, 145, 178, 0.1); }
.quick-item:nth-child(1) .quick-icon svg { color: #0891B2; }
.quick-item:nth-child(2) .quick-icon { background: rgba(5, 150, 105, 0.1); }
.quick-item:nth-child(2) .quick-icon svg { color: #059669; }
.quick-item:nth-child(3) .quick-icon { background: rgba(139, 92, 246, 0.1); }
.quick-item:nth-child(3) .quick-icon svg { color: #8B5CF6; }
.quick-item:nth-child(4) .quick-icon { background: rgba(245, 158, 11, 0.1); }
.quick-item:nth-child(4) .quick-icon svg { color: #F59E0B; }
.quick-item:nth-child(5) .quick-icon { background: rgba(8, 145, 178, 0.1); }
.quick-item:nth-child(5) .quick-icon svg { color: #0891B2; }
.quick-item:nth-child(6) .quick-icon { background: rgba(236, 72, 153, 0.1); }
.quick-item:nth-child(6) .quick-icon svg { color: #EC4899; }

.quick-name {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 2px;
  color: #1E293B;
}

.quick-desc {
  font-size: 11px;
  color: #94A3B8;
}

/* AI学姐 */
.ai-section {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
}

.ai-content {
  flex: 1;
}

.ai-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.ai-desc {
  font-size: 13px;
  color: #94A3B8;
}

.ai-action {
  padding: 12px 20px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.ai-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
}

@media (max-width: 640px) {
  .quick-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .today-courses {
    gap: 8px;
  }
  .course-chip {
    min-width: 120px;
    padding: 10px 12px;
  }
  .home-page {
    padding: 20px 16px 80px;
  }
}
</style>
