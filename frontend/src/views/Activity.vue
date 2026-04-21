<template>
  <div class="activity-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">校园活动</h1>
      <p class="page-subtitle">发现校园精彩活动</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-card">
      <div class="search-row">
        <div class="search-input-wrapper">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索活动..."
            class="search-input"
          />
        </div>
        <button class="filter-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="4" y1="21" x2="4" y2="14"/>
            <line x1="4" y1="10" x2="4" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12" y2="3"/>
            <line x1="20" y1="21" x2="20" y2="16"/>
            <line x1="20" y1="12" x2="20" y2="3"/>
          </svg>
        </button>
      </div>

      <!-- 分类标签 -->
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat"
          @click="selectedCategory = cat"
          :class="['tab-btn', { active: selectedCategory === cat }]"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- 活动列表 -->
    <div class="activity-list">
      <div
        v-for="activity in filteredActivities"
        :key="activity.id"
        class="activity-item"
      >
        <div class="activity-icon">
          <span>{{ activity.icon }}</span>
        </div>
        <div class="activity-content">
          <div class="activity-header">
            <h3>{{ activity.title }}</h3>
            <span :class="['status-badge', activity.statusClass]">
              {{ activity.status }}
            </span>
          </div>
          <p class="activity-desc">{{ activity.description }}</p>
          <div class="activity-meta">
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
                <line x1="9" y1="2" x2="9" y2="6"/>
                <line x1="15" y1="2" x2="15" y2="6"/>
              </svg>
              {{ activity.date }}
            </span>
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              {{ activity.location }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const selectedCategory = ref('全部')

const categories = ['全部', '学术', '文艺', '体育', '志愿服务', '创新创业', '社会实践']

const activities = ref([
  {
    id: 1,
    title: '第十届程序设计大赛',
    description: '面向全校学生的程序设计竞赛，考察算法和数据结构能力，优胜者将获得丰厚奖品和实习机会。',
    icon: '💻',
    status: '报名中',
    statusClass: 'registering',
    date: '2024-04-20',
    location: '计算机实验中心',
    category: '学术'
  },
  {
    id: 2,
    title: '校园歌手大赛',
    description: '展现歌喉的最佳舞台，无论是流行、摇滚还是民谣，这里都是你的主场。',
    icon: '🎤',
    status: '进行中',
    statusClass: 'ongoing',
    date: '2024-04-15',
    location: '大学生活动中心',
    category: '文艺'
  },
  {
    id: 3,
    title: '春季运动会',
    description: '田径、球类、趣味运动等多个项目，展现青春活力，争夺团体总分冠军。',
    icon: '🏃',
    status: '报名中',
    statusClass: 'registering',
    date: '2024-04-25',
    location: '校体育场',
    category: '体育'
  },
  {
    id: 4,
    title: '支教志愿者招募',
    description: '前往偏远山区学校进行为期一周的支教活动，现已开启报名。',
    icon: '📚',
    status: '报名中',
    statusClass: 'registering',
    date: '2024-05-01',
    location: '待定',
    category: '志愿服务'
  }
])

const filteredActivities = computed(() => {
  return activities.value.filter(a => {
    const matchSearch = a.title.includes(searchQuery.value) || a.description.includes(searchQuery.value)
    const matchCategory = selectedCategory.value === '全部' || a.category === selectedCategory.value
    return matchSearch && matchCategory
  })
})
</script>

<style scoped>
.activity-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #F5F1EB;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 15px;
  color: #A8A29E;
}

.search-card {
  background: #292524;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.search-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #78716C;
}

.search-input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: rgba(28, 25, 23, 0.8);
  border: 1px solid rgba(217, 119, 6, 0.15);
  border-radius: 10px;
  color: #F5F1EB;
  font-size: 15px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #D97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
}

.search-input::placeholder {
  color: #78716C;
}

.filter-btn {
  width: 44px;
  height: 44px;
  background: rgba(217, 119, 6, 0.1);
  border: 1px solid rgba(217, 119, 6, 0.2);
  border-radius: 10px;
  color: #D97706;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: rgba(217, 119, 6, 0.15);
}

.category-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.tab-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 20px;
  color: #A8A29E;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  border-color: rgba(217, 119, 6, 0.2);
  color: #D6D3D1;
}

.tab-btn.active {
  background: rgba(217, 119, 6, 0.15);
  border-color: rgba(217, 119, 6, 0.3);
  color: #D97706;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 18px;
  background: #292524;
  border: 1px solid rgba(217, 119, 6, 0.1);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.activity-item:hover {
  border-color: rgba(217, 119, 6, 0.2);
  transform: translateY(-2px);
}

.activity-icon {
  width: 56px;
  height: 56px;
  background: rgba(217, 119, 6, 0.1);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.activity-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #F5F1EB;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.status-badge.registering {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.status-badge.ongoing {
  background: rgba(2, 132, 199, 0.1);
  color: #0284C7;
}

.status-badge.ended {
  background: rgba(168, 85, 247, 0.1);
  color: #A855F7;
}

.activity-desc {
  font-size: 14px;
  color: #A8A29E;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.activity-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #78716C;
}
</style>
