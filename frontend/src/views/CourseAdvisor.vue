<template>
  <div class="course-advisor-page">
    <!-- 返回和标题 -->
    <div class="page-header">
      <router-link to="/" class="back-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </router-link>
      <div class="header-text">
        <h1 class="page-title">选课助手</h1>
        <p class="page-subtitle">AI帮你找到最合适的课程</p>
      </div>
    </div>

    <!-- AI推荐卡片 -->
    <div class="advisor-card">
      <div class="advisor-header">
        <div class="advisor-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
        </div>
        <div class="advisor-info">
          <h2>智能选课推荐</h2>
          <p>基于你的专业和兴趣，AI为你推荐合适的课程</p>
        </div>
      </div>

      <!-- 学期选择 -->
      <div class="form-group">
        <label>选择学期</label>
        <select class="form-select" v-model="selectedSemester">
          <option value="2024-1">2023-2024学年 第二学期</option>
          <option value="2023-2">2023-2024学年 第一学期</option>
          <option value="2023-1">2022-2023学年 第二学期</option>
        </select>
      </div>

      <!-- 专业选择 -->
      <div class="form-group">
        <label>我的专业</label>
        <select class="form-select" v-model="selectedMajor">
          <option value="cs">计算机科学与技术</option>
          <option value="se">软件工程</option>
          <option value="ds">数据科学与大数据技术</option>
        </select>
      </div>

      <button class="recommend-btn" @click="getRecommendations">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        </svg>
        获取推荐
      </button>
    </div>

    <!-- 推荐课程列表 -->
    <div class="recommendations-section">
      <h2 class="section-title">为你推荐</h2>

      <div class="course-list">
        <div v-for="course in recommendedCourses" :key="course.id" class="course-card">
          <div class="course-main">
            <div class="course-header">
              <h3>{{ course.name }}</h3>
              <div class="course-rating">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#D97706">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                <span>{{ course.rating }}</span>
              </div>
            </div>
            <p class="course-meta">{{ course.teacher }} · {{ course.credits }}学分</p>
            <p class="course-desc">{{ course.description }}</p>

            <div class="course-tags">
              <span v-for="tag in course.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <div class="course-footer">
            <span class="enrollment">{{ course.enrolled }}/{{ course.capacity }}已选</span>
            <button class="detail-btn">查看详情</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const selectedSemester = ref('2024-1')
const selectedMajor = ref('cs')

const recommendedCourses = ref([
  {
    id: 1,
    name: '人工智能导论',
    teacher: '张教授',
    credits: 3,
    rating: 4.9,
    reviews: 328,
    description: '介绍人工智能的基本概念、发展历程和核心技术，包括机器学习、深度学习、自然语言处理等方向。',
    tags: ['热门', '核心课', '实践性强'],
    enrolled: 85,
    capacity: 100
  },
  {
    id: 2,
    name: '计算机网络',
    teacher: '李教授',
    credits: 3,
    rating: 4.7,
    reviews: 256,
    description: '系统讲解计算机网络的基本原理、协议栈和实际应用，涵盖TCP/IP、HTTP、DNS等重要知识点。',
    tags: ['必修', '考研相关'],
    enrolled: 92,
    capacity: 100
  },
  {
    id: 3,
    name: '数据库系统概论',
    teacher: '王老师',
    credits: 3,
    rating: 4.8,
    reviews: 289,
    description: '数据库系统的基本概念、关系模型、SQL语言、数据库设计和事务管理等内容。',
    tags: ['必修', '就业必备'],
    enrolled: 78,
    capacity: 90
  }
])

function getRecommendations() {
  alert('推荐功能开发中...')
}
</script>

<style scoped>
.course-advisor-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.back-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #292524;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 12px;
  color: #A8A29E;
  text-decoration: none;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(217, 119, 6, 0.1);
  color: #D97706;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #F5F1EB;
  margin-bottom: 2px;
}

.page-subtitle {
  font-size: 14px;
  color: #A8A29E;
}

.advisor-card {
  background: #292524;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 28px;
}

.advisor-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(217, 119, 6, 0.1);
}

.advisor-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #D97706, #F59E0B);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1C1917;
  flex-shrink: 0;
}

.advisor-info h2 {
  font-size: 18px;
  font-weight: 600;
  color: #F5F1EB;
  margin-bottom: 4px;
}

.advisor-info p {
  font-size: 14px;
  color: #A8A29E;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #A8A29E;
  margin-bottom: 8px;
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  background: rgba(28, 25, 23, 0.8);
  border: 1px solid rgba(217, 119, 6, 0.15);
  border-radius: 10px;
  color: #F5F1EB;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-select:focus {
  outline: none;
  border-color: #D97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
}

.recommend-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: linear-gradient(135deg, #D97706, #F59E0B);
  border: none;
  border-radius: 12px;
  color: #1C1917;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.recommend-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);
}

.recommendations-section {
  margin-top: 28px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #F5F1EB;
  margin-bottom: 16px;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-card {
  background: #292524;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.2s ease;
}

.course-card:hover {
  border-color: rgba(217, 119, 6, 0.2);
  transform: translateY(-2px);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.course-header h3 {
  font-size: 17px;
  font-weight: 600;
  color: #F5F1EB;
}

.course-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #D97706;
}

.course-meta {
  font-size: 13px;
  color: #A8A29E;
  margin-bottom: 10px;
}

.course-desc {
  font-size: 14px;
  color: #D6D3D1;
  line-height: 1.6;
  margin-bottom: 14px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 4px 12px;
  background: rgba(217, 119, 6, 0.1);
  border-radius: 20px;
  font-size: 12px;
  color: #D97706;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 14px;
  border-top: 1px solid rgba(217, 119, 6, 0.08);
}

.enrollment {
  font-size: 13px;
  color: #78716C;
}

.detail-btn {
  padding: 8px 16px;
  background: rgba(217, 119, 6, 0.1);
  border: 1px solid rgba(217, 119, 6, 0.2);
  border-radius: 8px;
  color: #D97706;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.detail-btn:hover {
  background: rgba(217, 119, 6, 0.15);
  border-color: rgba(217, 119, 6, 0.3);
}
</style>
