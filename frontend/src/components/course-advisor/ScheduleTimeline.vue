<template>
  <div class="schedule-timeline" :class="{ collapsed: isCollapsed }">
    <div class="timeline-header">
      <h3 class="timeline-title">选课时间表</h3>
      <div class="header-actions">
        <span class="credits-total">已选 {{ selectedCredits }} 学分</span>
        <button class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <svg v-if="isCollapsed" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-show="!isCollapsed" class="timeline-content">
      <!-- 星期导航 -->
      <div class="week-nav">
        <button
          v-for="day in weekDays"
          :key="day.value"
          class="day-btn"
          :class="{ active: selectedDay === day.value }"
          @click="selectedDay = day.value"
        >
          <span class="day-name">{{ day.name }}</span>
        </button>
      </div>

      <!-- 时间轴 -->
      <div class="time-axis">
        <div
          v-for="slot in 12"
          :key="slot"
          class="time-slot"
        >
          <div class="slot-time">{{ formatSlot(slot) }}</div>
          <div class="slot-content">
            <div
              v-for="course in getCoursesAtSlot(slot)"
              :key="course.id"
              class="slot-course"
              :class="{ conflict: course.conflict_status !== 'none' }"
              :style="{ backgroundColor: getCourseColor(course.id) }"
            >
              <span class="course-name">{{ course.name }}</span>
              <span class="course-location">{{ course.location || '' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 冲突提示 -->
      <div v-if="conflicts.length > 0" class="conflict-list">
        <div class="conflict-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>时间冲突</span>
        </div>
        <div
          v-for="conflict in conflicts"
          :key="conflict.id"
          class="conflict-item"
        >
          <span class="conflict-time">{{ formatConflictTime(conflict) }}</span>
          <span class="conflict-courses">{{ conflict.course1 }} 与 {{ conflict.course2 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  selectedCourses: {
    type: Array,
    default: () => []
  },
  conflicts: {
    type: Array,
    default: () => []
  }
})

const isCollapsed = ref(false)
const selectedDay = ref(1)
const selectedCredits = computed(() =>
  props.selectedCourses.reduce((sum, c) => sum + (c.credits || 0), 0)
)

const weekDays = [
  { name: '周一', value: 1 },
  { name: '周二', value: 2 },
  { name: '周三', value: 3 },
  { name: '周四', value: 4 },
  { name: '周五', value: 5 },
  { name: '周六', value: 6 },
  { name: '周日', value: 7 }
]

const courseColors = [
  'rgba(8, 145, 178, 0.3)',
  'rgba(139, 92, 246, 0.3)',
  'rgba(5, 150, 105, 0.3)',
  'rgba(245, 158, 11, 0.3)',
  'rgba(239, 68, 68, 0.3)'
]

function formatSlot(slot) {
  const sessions = {
    1: '1-2节', 2: '1-2节',
    3: '3-4节', 4: '3-4节',
    5: '5-6节', 6: '5-6节',
    7: '7-8节', 8: '7-8节',
    9: '9-10节', 10: '9-10节',
    11: '11-12节', 12: '11-12节'
  }
  return sessions[slot] || `${slot}`
}

function getCoursesAtSlot(slot) {
  return props.selectedCourses.filter(course =>
    course.day_of_week === selectedDay.value &&
    course.start_slot <= slot &&
    course.end_slot >= slot
  )
}

function getCourseColor(courseId) {
  const index = courseId % courseColors.length
  return courseColors[index]
}

function formatConflictTime(conflict) {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return `${days[conflict.day || 1]} ${conflict.startSlot}-${conflict.endSlot}节`
}
</script>

<style scoped>
.schedule-timeline {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 16px;
}

.schedule-timeline.collapsed {
  padding-bottom: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.schedule-timeline.collapsed .timeline-header {
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}

.credits-total {
  font-size: 13px;
  color: #0891B2;
  font-weight: 500;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
  cursor: pointer;
  color: #64748B;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: #F1F5F9;
  color: #0891B2;
}

.week-nav {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  overflow-x: auto;
}

.day-btn {
  flex: 1;
  min-width: 40px;
  padding: 8px 4px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.day-btn.active {
  background: #0891B2;
  border-color: #0891B2;
  color: #fff;
}

.day-name {
  font-size: 12px;
  font-weight: 500;
}

.time-axis {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-slot {
  display: flex;
  gap: 12px;
}

.slot-time {
  width: 50px;
  font-size: 11px;
  color: #94A3B8;
  padding-top: 4px;
}

.slot-content {
  flex: 1;
  min-height: 32px;
  background: #F8FAFC;
  border-radius: 6px;
  padding: 4px;
}

.slot-course {
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
}

.slot-course.conflict {
  border: 1px solid #EF4444;
}

.course-name {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #1E293B;
}

.course-location {
  display: block;
  font-size: 10px;
  color: #64748B;
}

.conflict-list {
  margin-top: 16px;
  padding: 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
}

.conflict-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #F59E0B;
  margin-bottom: 8px;
}

.conflict-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid rgba(245, 158, 11, 0.2);
}

.conflict-item:last-child {
  border-bottom: none;
}

.conflict-time {
  color: #64748B;
}

.conflict-courses {
  color: #475569;
  font-weight: 500;
}
</style>
