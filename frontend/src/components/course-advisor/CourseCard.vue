<template>
  <div
    class="course-card"
    :class="{ 'has-conflict': conflictStatus !== 'none', 'is-selected': isSelected }"
    @click="$emit('click', course)"
  >
    <!-- 冲突警告 -->
    <div v-if="conflictStatus === 'error'" class="conflict-banner error">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      <span>{{ conflictInfo }}</span>
    </div>
    <div v-else-if="conflictStatus === 'warning'" class="conflict-banner warning">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <span>{{ conflictInfo }}</span>
    </div>

    <!-- 课程头部 -->
    <div class="card-header">
      <div class="course-info">
        <h3 class="course-name">{{ course.name }}</h3>
        <div class="course-meta">
          <span class="teacher">{{ course.teacher }}</span>
          <span class="separator">·</span>
          <span class="credits">{{ course.credits }}学分</span>
          <span class="separator">·</span>
          <span class="schedule">{{ formatSchedule(course) }}</span>
        </div>
      </div>
      <div class="course-rating">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="#D97706">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        <span>{{ course.rating }}</span>
      </div>
    </div>

    <!-- 匹配进度 -->
    <div v-if="course.match_reason" class="match-section">
      <div class="match-header">
        <span class="match-label">匹配度</span>
        <span class="match-value">{{ matchPercentage }}%</span>
      </div>
      <div class="match-bar">
        <div class="match-fill" :style="{ width: matchPercentage + '%' }" />
      </div>
    </div>

    <!-- 推荐理由 -->
    <p v-if="course.match_reason" class="match-reason">
      {{ course.match_reason }}
    </p>

    <!-- 标签 -->
    <div class="course-tags">
      <span
        v-for="tag in course.tags"
        :key="tag"
        class="tag"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 选课人数 -->
    <div class="enrollment-info">
      <div class="enrollment-bar">
        <div
          class="enrollment-fill"
          :style="{ width: (course.enrolled / course.capacity * 100) + '%' }"
        />
      </div>
      <span class="enrollment-text">{{ course.enrolled }}/{{ course.capacity }} 已选 | 剩余 {{ availableSlots }} 名额</span>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions">
      <button
        v-if="availableSlots > 0"
        class="action-btn select-btn"
        :class="{ selected: isSelected, cancel: isSelected }"
        @click.stop="toggleSelection"
      >
        <svg v-if="isSelected" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
        <span>{{ isSelected ? '取消' : '选择' }}</span>
      </button>
      <button v-else class="action-btn select-btn" disabled>
        <span>已满</span>
      </button>
      <button class="action-btn detail-btn" @click.stop="$emit('showDetail', course)">
        详情
      </button>
      <button class="action-btn reason-btn" @click.stop="$emit('showReason', course)">
        推荐理由
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'showDetail', 'showReason', 'toggleSelect'])

const conflictStatus = computed(() => props.course.conflict_status || 'none')
const conflictInfo = computed(() => props.course.conflict_info || '')
const availableSlots = computed(() => {
  const capacity = props.course.capacity || 100
  const enrolled = props.course.enrolled || 0
  return Math.max(0, capacity - enrolled)
})

const matchPercentage = computed(() => {
  // 根据匹配理由长度和课程评分估算匹配度
  const baseScore = props.course.rating * 20
  return Math.min(95, Math.max(60, Math.round(baseScore)))
})

function formatSchedule(course) {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const day = days[course.day_of_week] || '未知'
  return `${day} ${course.start_slot}-${course.end_slot}节`
}

function toggleSelection() {
  emit('toggleSelect', props.course.id)
}
</script>

<style scoped>
.course-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.course-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.course-card.has-conflict {
  border-color: #F59E0B;
}

.course-card.is-selected {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.03);
}

.conflict-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 12px;
}

.conflict-banner.error {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.conflict-banner.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.course-name {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #64748B;
}

.separator {
  color: #CBD5E1;
}

.course-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #D97706;
}

.match-section {
  margin-bottom: 8px;
}

.match-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.match-label {
  font-size: 12px;
  color: #64748B;
}

.match-value {
  font-size: 12px;
  font-weight: 600;
  color: #0891B2;
}

.match-bar {
  height: 6px;
  background: #E2E8F0;
  border-radius: 3px;
  overflow: hidden;
}

.match-fill {
  height: 100%;
  background: linear-gradient(90deg, #0891B2, #22D3EE);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.match-reason {
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
  margin: 12px 0;
  padding: 10px;
  background: #F8FAFC;
  border-radius: 8px;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.tag {
  padding: 4px 10px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 12px;
  font-size: 12px;
  color: #0891B2;
}

.enrollment-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.enrollment-bar {
  flex: 1;
  height: 4px;
  background: #E2E8F0;
  border-radius: 2px;
  overflow: hidden;
}

.enrollment-fill {
  height: 100%;
  background: #059669;
  border-radius: 2px;
}

.enrollment-text {
  font-size: 12px;
  color: #64748B;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #F1F5F9;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.select-btn {
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  color: #0891B2;
}

.select-btn.selected {
  background: #0891B2;
  border-color: #0891B2;
  color: #fff;
}

.select-btn.cancel {
  background: #EF4444;
  border-color: #EF4444;
  color: #fff;
}

.select-btn.cancel:hover {
  background: #DC2626;
}

.select-btn:disabled {
  background: #E2E8F0;
  border-color: #E2E8F0;
  color: #94A3B8;
  cursor: not-allowed;
}

.select-btn:hover {
  background: rgba(8, 145, 178, 0.15);
}

.detail-btn {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  color: #64748B;
}

.detail-btn:hover {
  background: #F1F5F9;
  color: #475569;
}

.reason-btn {
  background: transparent;
  border: 1px solid #E2E8F0;
  color: #64748B;
}

.reason-btn:hover {
  background: #F8FAFC;
  color: #0891B2;
  border-color: #0891B2;
}
</style>