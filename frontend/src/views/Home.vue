<template>
  <div class="home-page">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <p class="greeting">{{ greeting }}，同学</p>
        <h1 class="welcome-title">今天有什么需要帮忙的？</h1>
      </div>
      <div class="welcome-avatar">
        <div class="avatar-circle">
          <span>AI</span>
        </div>
      </div>
    </div>

    <!-- 快捷功能 -->
    <div class="section">
      <h2 class="section-title">快捷服务</h2>
      <div class="quick-actions">
        <router-link to="/timetable" class="action-card">
          <div class="action-icon" style="background: rgba(8, 145, 178, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>课表管理</h3>
            <p>查看和导入课程</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>

        <router-link to="/ai-sister" class="action-card">
          <div class="action-icon" style="background: rgba(5, 150, 105, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>AI学姐</h3>
            <p>智能对话助手</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>

        <router-link to="/review" class="action-card">
          <div class="action-icon" style="background: rgba(8, 145, 178, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>录音回顾</h3>
            <p>转写与智能总结</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>

        <router-link to="/course-advisor" class="action-card">
          <div class="action-icon" style="background: rgba(8, 145, 178, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>选课助手</h3>
            <p>智能选课推荐</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>

        <router-link to="/translate" class="action-card">
          <div class="action-icon" style="background: rgba(139, 92, 246, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>智能翻译</h3>
            <p>即时翻译文档导出</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>

        <router-link to="/activity" class="action-card">
          <div class="action-icon" style="background: rgba(245, 158, 11, 0.1);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
          </div>
          <div class="action-info">
            <h3>活动助手</h3>
            <p>策划方案与文案生成</p>
          </div>
          <svg class="action-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </router-link>
      </div>
    </div>

    <!-- 今日课程 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">今日课程</h2>
        <span v-if="className" class="class-badge">{{ className }}</span>
        <router-link to="/timetable" class="section-link">查看全部</router-link>
      </div>
      <div class="course-list">
        <div v-if="courses.length > 0" v-for="course in courses" :key="course.id" class="course-card">
          <div class="course-time">
            <span class="time-range">{{ course.time }}</span>
            <span class="course-slot">第{{ course.start_slot }}-{{ course.end_slot }}节</span>
          </div>
          <div class="course-info">
            <h3>{{ course.name }}</h3>
            <p>{{ course.location || '未指定地点' }}</p>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <p>今天没有课程安排</p>
          <router-link to="/timetable/import" class="btn-link">导入课表</router-link>
        </div>
      </div>
    </div>

    <!-- AI 对话入口 -->
    <div class="section">
      <div class="ai-card">
        <div class="ai-content">
          <div class="ai-avatar">
            <img src="/images/sisiter-avatar.jpg" alt="AI学姐" class="sisiter-avatar-round" />
          </div>
          <div class="ai-text">
            <h3>有问题？问问AI学姐</h3>
            <p>可以帮你查课表、问选课、了解校园信息...</p>
          </div>
        </div>
        <router-link to="/ai-sister" class="ai-btn">
          开始对话
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTimetableStore } from '@/stores/timetable'

const timetableStore = useTimetableStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const courses = computed(() => timetableStore.todayCourses)
const className = computed(() => timetableStore.className)

onMounted(async () => {
  await timetableStore.fetchTodayData()
})
</script>

<style scoped>
.home-page {
  padding: 24px 40px;
  background: #F8FAFC;
  min-height: 100vh;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.greeting {
  font-size: 15px;
  color: #64748B;
  margin-bottom: 4px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
}

.avatar-circle {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: white;
}

.section {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.class-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border-radius: 20px;
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 500;
}

.section-link {
  font-size: 14px;
  color: #0891B2;
  text-decoration: none;
}

.section-link:hover { text-decoration: underline; }

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-card:hover {
  border-color: #0891B2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.action-info {
  flex: 1;
}

.action-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 2px;
}

.action-info p {
  font-size: 13px;
  color: #64748B;
}

.action-arrow {
  color: #CBD5E1;
  flex-shrink: 0;
}

.course-list { display: flex; flex-direction: column; gap: 12px; }

.course-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.course-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}

.time-range {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.course-slot {
  font-size: 12px;
  color: #64748B;
}

.course-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.course-info p {
  font-size: 13px;
  color: #64748B;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  background: #FFFFFF;
  border: 1px dashed #E2E8F0;
  border-radius: 16px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: rgba(8, 145, 178, 0.08);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon svg {
  stroke: #0891B2;
}

.empty-state p {
  color: #64748B;
  margin-bottom: 12px;
}

.btn-link {
  color: #0891B2;
  font-size: 14px;
  text-decoration: none;
}

.btn-link:hover { text-decoration: underline; }

.ai-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08), rgba(34, 211, 238, 0.04));
  border: 1px solid rgba(8, 145, 178, 0.12);
  border-radius: 20px;
}

.ai-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-avatar {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  overflow: hidden;
}

.sisiter-avatar-round {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 50%;
}

.ai-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.ai-text p {
  font-size: 14px;
  color: #64748B;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  color: white;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.ai-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}
</style>
