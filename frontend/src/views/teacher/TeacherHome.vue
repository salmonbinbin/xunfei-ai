<template>
  <div class="teacher-home">
    <!-- 主内容区 -->
    <main class="main-content">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎，{{ userStore.userInfo?.name || '老师' }}！</h1>
        <p class="welcome-subtitle">选择功能模块开始智能教学之旅</p>
      </div>

      <div class="cards-grid">
        <!-- 成绩管理卡片 -->
        <div class="feature-card" @click="handleCardClick('grade')">
          <div class="card-icon grade-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <div class="card-info">
            <div class="card-title-row">
              <h3 class="card-title">成绩管理</h3>
              <el-tag size="small" type="warning" effect="plain" class="badge">待开发</el-tag>
            </div>
            <p class="card-subtitle">智能分析 · Excel上传 · 可视化图表</p>
          </div>
          <div class="card-arrow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>

        <!-- 通知发布卡片 -->
        <div class="feature-card" @click="handleCardClick('notification')">
          <div class="card-icon notification-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <div class="card-info">
            <div class="card-title-row">
              <h3 class="card-title">通知发布</h3>
              <el-tag size="small" type="warning" effect="plain" class="badge">待开发</el-tag>
            </div>
            <p class="card-subtitle">AI生成 · 格式规范 · 一键发布</p>
          </div>
          <div class="card-arrow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>

        <!-- 备课教案卡片 -->
        <div class="feature-card" @click="handleCardClick('lesson-plan')">
          <div class="card-icon lesson-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <div class="card-info">
            <div class="card-title-row">
              <h3 class="card-title">备课教案</h3>
              <el-tag size="small" type="warning" effect="plain" class="badge">待开发</el-tag>
            </div>
            <p class="card-subtitle">AI生成大纲 · PPT自动制作 · 教学建议</p>
          </div>
          <div class="card-arrow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>
      </div>

      <div class="tips-section">
        <div class="tips-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4m0-4h.01"/>
          </svg>
        </div>
        <p class="tips-text">教师端功能正在陆续开发中，敬请期待！</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

function handleCardClick(type) {
  router.push(`/teacher/${type}`)
}
</script>

<style scoped>
.teacher-home {
  min-height: 100vh;
  background: #F8FAFC;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.welcome-section {
  margin-bottom: 40px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px;
}

.welcome-subtitle {
  font-size: 16px;
  color: #64748B;
  margin: 0;
}

.cards-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: #0891B2;
  box-shadow: 0 8px 24px rgba(8, 145, 178, 0.08);
  transform: translateY(-2px);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.grade-icon {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.1), rgba(34, 211, 238, 0.1));
  color: #0891B2;
}

.notification-icon {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(167, 139, 250, 0.1));
  color: #8B5CF6;
}

.lesson-icon {
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(52, 211, 153, 0.1));
  color: #059669;
}

.card-info {
  flex: 1;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

.card-subtitle {
  font-size: 14px;
  color: #94A3B8;
  margin: 0;
}

.card-arrow {
  color: #CBD5E1;
  transition: all 0.2s ease;
}

.feature-card:hover .card-arrow {
  color: #0891B2;
  transform: translateX(4px);
}

.tips-section {
  margin-top: 32px;
  padding: 16px 20px;
  background: rgba(8, 145, 178, 0.04);
  border: 1px solid rgba(8, 145, 178, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tips-icon {
  color: #0891B2;
}

.tips-text {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .brand-text {
    font-size: 16px;
  }

  .main-content {
    padding: 24px 16px 80px;
  }

  .welcome-title {
    font-size: 24px;
  }

  .feature-card {
    padding: 20px;
  }

  .card-icon {
    width: 48px;
    height: 48px;
  }

  .card-title {
    font-size: 16px;
  }
}
</style>
