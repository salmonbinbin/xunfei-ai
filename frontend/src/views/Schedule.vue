<template>
  <div class="schedule-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">我的日程</h1>
        <p class="page-subtitle">合理安排时间，让学习更高效</p>
      </div>
      <button class="add-btn" @click="showAddModal = true">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        添加日程
      </button>
    </div>

    <!-- 日历视图 -->
    <div class="calendar-card">
      <div class="calendar-header">
        <button class="nav-btn" @click="prevMonth">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="current-month">{{ currentMonth }}</span>
        <button class="nav-btn" @click="nextMonth">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>

      <!-- 星期标题 -->
      <div class="weekdays">
        <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
      </div>

      <!-- 日期网格 -->
      <div class="days-grid">
        <div
          v-for="(date, index) in calendarDays"
          :key="index"
          :class="[
            'day-cell',
            { 'is-empty': date.isEmpty },
            { 'is-today': date.isToday },
            { 'is-selected': isSelected(date) },
            { 'has-schedule': date.hasSchedule }
          ]"
          @click="selectDate(date)"
        >
          <span class="day-number">{{ date.day }}</span>
          <div v-if="date.hasSchedule" class="schedule-dot"></div>
        </div>
      </div>
    </div>

    <!-- 选中日期的日程 -->
    <div class="schedule-section">
      <div class="section-header">
        <h2 class="section-title">{{ selectedDateLabel }}</h2>
        <button class="ai-add-btn" @click="showAIAdd = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          </svg>
          AI智能添加
        </button>
      </div>

      <div v-if="selectedSchedules.length > 0" class="schedule-list">
        <div
          v-for="schedule in selectedSchedules"
          :key="schedule.id"
          class="schedule-item"
        >
          <div class="schedule-color" :style="{ background: getCategoryColor(schedule.category) }"></div>
          <div class="schedule-content">
            <h3>{{ schedule.title }}</h3>
            <div class="schedule-meta">
              <span class="schedule-time">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                {{ schedule.time }}
              </span>
              <span v-if="schedule.location" class="schedule-location">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {{ schedule.location }}
              </span>
            </div>
          </div>
          <button class="delete-btn" @click="deleteSchedule(schedule.id)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#78716C" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
            <line x1="9" y1="2" x2="9" y2="6"/>
            <line x1="15" y1="2" x2="15" y2="6"/>
          </svg>
        </div>
        <p>当日暂无日程安排</p>
        <button class="add-first-btn" @click="showAddModal = true">添加第一个日程</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSchedules, deleteSchedule as deleteScheduleApi, createSchedule } from '@/api/schedule'

const showAddModal = ref(false)
const showAIAdd = ref(false)
const currentDate = ref(new Date())
const selectedDate = ref(new Date())

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const schedules = ref([])

// 有日程的日期（用于显示小圆点）
const scheduleDates = computed(() => {
  return schedules.value.map(s => {
    const d = new Date(s.date) || new Date()
    return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
  })
})

const currentMonth = computed(() => {
  return currentDate.value.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })
})

const selectedDateLabel = computed(() => {
  const date = selectedDate.value
  const today = new Date()
  const isToday = date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()

  if (isToday) {
    return '今天'
  }
  return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })
})

const selectedSchedules = computed(() => {
  return schedules.value.filter(s => {
    const d = new Date(s.date)
    return d.getDate() === selectedDate.value.getDate() &&
      d.getMonth() === selectedDate.value.getMonth() &&
      d.getFullYear() === selectedDate.value.getFullYear()
  })
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const days = []

  for (let i = 0; i < firstDay.getDay(); i++) {
    days.push({ day: '', isEmpty: true })
  }

  for (let i = 1; i <= lastDay.getDate(); i++) {
    const today = new Date()
    const date = new Date(year, month, i)
    const dateKey = `${year}-${month}-${i}`
    days.push({
      day: i,
      isToday: today.getDate() === i && today.getMonth() === month && today.getFullYear() === year,
      isEmpty: false,
      date: date,
      hasSchedule: scheduleDates.value.includes(dateKey)
    })
  }

  return days
})

function isSelected(date) {
  if (date.isEmpty) return false
  return date.date.getDate() === selectedDate.value.getDate() &&
    date.date.getMonth() === selectedDate.value.getMonth() &&
    date.date.getFullYear() === selectedDate.value.getFullYear()
}

function getCategoryColor(category) {
  const colors = {
    meeting: '#D97706',
    study: '#059669',
    activity: '#0284C7',
    other: '#A855F7'
  }
  return colors[category] || colors.other
}

function prevMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1)
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1)
}

function selectDate(date) {
  if (date.isEmpty) return
  selectedDate.value = date.date
}

async function loadSchedules() {
  try {
    const res = await getSchedules()
    schedules.value = res.data || []
  } catch (error) {
    console.error('[Schedule] Failed to load schedules:', error)
  }
}

async function deleteSchedule(id) {
  try {
    await deleteScheduleApi(id)
    schedules.value = schedules.value.filter(s => s.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function handleAIAdd() {
  // AI智能添加日程
  ElMessage.info('AI智能添加功能开发中')
}

onMounted(async () => {
  await loadSchedules()
})
</script>

<style scoped>
.schedule-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  background: #F8FAFC;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 15px;
  color: #64748B;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35);
}

.calendar-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.nav-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #F0FDFA;
  border-color: #0891B2;
  color: #0891B2;
}

.current-month {
  font-size: 17px;
  font-weight: 600;
  color: #1E293B;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  font-weight: 500;
  color: #94A3B8;
  padding: 8px 0;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.day-cell:not(.is-empty):hover {
  background: #F0FDFA;
}

.day-cell.is-empty {
  cursor: default;
}

.day-cell.is-today .day-number {
  background: #0891B2;
  color: white;
}

.day-cell.is-selected {
  background: #F0FDFA;
  border: 1px solid rgba(8, 145, 178, 0.3);
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.schedule-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #0891B2;
  position: absolute;
  bottom: 6px;
}

.schedule-section {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #1E293B;
}

.ai-add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(5, 150, 105, 0.1);
  border: 1px solid rgba(5, 150, 105, 0.2);
  border-radius: 8px;
  color: #059669;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ai-add-btn:hover {
  background: rgba(5, 150, 105, 0.15);
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.schedule-item:hover {
  border-color: rgba(8, 145, 178, 0.2);
}

.schedule-color {
  width: 4px;
  height: 44px;
  border-radius: 2px;
  flex-shrink: 0;
}

.schedule-content {
  flex: 1;
}

.schedule-content h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.schedule-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.schedule-time,
.schedule-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #64748B;
}

.delete-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #94A3B8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #EF4444;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
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

.empty-state p {
  color: #64748B;
  margin-bottom: 16px;
}

.add-first-btn {
  padding: 10px 20px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 10px;
  color: #0891B2;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-first-btn:hover {
  background: rgba(8, 145, 178, 0.15);
  border-color: rgba(8, 145, 178, 0.3);
}
</style>
