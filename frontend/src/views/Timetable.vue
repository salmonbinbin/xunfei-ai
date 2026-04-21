<template>
  <div class="timetable-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">我的课表</h1>
        <p class="page-subtitle">第{{ currentWeek }}周 · {{ semesterLabel }}</p>
      </div>
      <router-link to="/timetable/import" class="import-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        导入课表
      </router-link>
    </div>

    <!-- 周选择器 -->
    <div class="week-selector-card">
      <div class="week-nav">
        <button class="nav-btn" @click="prevWeek">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="week-label">第{{ currentWeek }}周</span>
        <button class="nav-btn" @click="nextWeek">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>

      <!-- 星期选择 -->
      <div class="week-days">
        <button
          v-for="(day, index) in weekDays"
          :key="index"
          @click="selectedDay = index"
          :class="['day-btn', { active: selectedDay === index, isToday: day.isToday }]"
        >
          <span class="day-short">{{ day.short }}</span>
          <span class="day-date">{{ day.date }}</span>
        </button>
      </div>
    </div>

    <!-- 课程列表 -->
    <div class="course-list">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-item"
        @click="showCourseDetail(course)"
      >
        <div class="course-time-col">
          <span class="course-slot">第{{ course.start_slot }}-{{ course.end_slot }}节</span>
        </div>
        <div class="course-info-col">
          <h3>{{ course.name }}</h3>
          <div class="course-meta">
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              {{ course.location || '地点待定' }}
            </span>
            </div>
        </div>
        <svg class="arrow-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredCourses.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#78716C" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
            <line x1="9" y1="2" x2="9" y2="6"/>
            <line x1="15" y1="2" x2="15" y2="6"/>
          </svg>
        </div>
        <p>当日暂无课程</p>
        <router-link to="/timetable/import" class="empty-action">导入课表</router-link>
      </div>
    </div>

    <!-- AI建议抽屉 -->
    <el-drawer v-model="showAIInsight" title="AI学习助手" size="400px" direction="rtl">
      <div v-if="selectedCourse" class="ai-drawer-content">
        <div class="course-header">
          <h3>{{ selectedCourse.name }}</h3>
          <p class="course-info-text">
            {{ getDayName(selectedCourse.day_of_week) }} 第{{ selectedCourse.start_slot }}-{{ selectedCourse.end_slot }}节
            <span v-if="selectedCourse.location"> | {{ selectedCourse.location }}</span>
          </p>
        </div>

        <!-- AI洞察内容 -->
        <div v-if="selectedCourse.ai_insight" class="ai-insight">
          <div class="insight-section">
            <h4>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
              课程概述
            </h4>
            <p>{{ selectedCourse.ai_insight.course_summary }}</p>
          </div>

          <div class="insight-section">
            <h4>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
              学习建议
            </h4>
            <ul class="tips-list">
              <li v-for="(tip, idx) in selectedCourse.ai_insight.learning_tips" :key="idx">{{ tip }}</li>
            </ul>
          </div>

          <div class="insight-section">
            <h4>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
              课前预习
            </h4>
            <p>{{ selectedCourse.ai_insight.preview_suggestion }}</p>
          </div>

          <div class="insight-section">
            <h4>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              课后复习
            </h4>
            <p>{{ selectedCourse.ai_insight.review_suggestion }}</p>
          </div>

          <div class="insight-section">
            <h4>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              核心知识点
            </h4>
            <div class="key-points">
              <el-tag v-for="(point, idx) in selectedCourse.ai_insight.key_points" :key="idx" size="small" class="point-tag">
                {{ point }}
              </el-tag>
            </div>
          </div>

          <div class="insight-tags">
            <el-tag :type="getDifficultyType(selectedCourse.ai_insight.difficulty_level)">
              难度: {{ getDifficultyLabel(selectedCourse.ai_insight.difficulty_level) }}
            </el-tag>
            <el-tag :type="getImportanceType(selectedCourse.ai_insight.importance)">
              重要性: {{ getImportanceLabel(selectedCourse.ai_insight.importance) }}
            </el-tag>
          </div>
        </div>

        <!-- 生成AI建议按钮 -->
        <div v-else class="generate-section">
          <p class="generate-hint">点击按钮，让AI为这门课程生成学习建议</p>
          <button class="generate-btn" @click="handleGenerateInsights" :disabled="insightLoading">
            <span v-if="insightLoading" class="loading-content">
              <svg class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
              </svg>
              生成中...
            </span>
            <span v-else>生成AI学习建议</span>
          </button>
        </div>

        <!-- AI问答区域 -->
        <div class="ai-chat-section">
          <h4>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            问问AI学伴
          </h4>
          <div class="chat-input-wrapper">
            <input
              v-model="chatQuestion"
              type="text"
              placeholder="输入你的问题..."
              class="chat-input"
              @keyup.enter="sendChat"
            />
            <button class="send-btn" @click="sendChat" :disabled="!chatQuestion.trim() || chatLoading">
              <svg v-if="!chatLoading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
              <svg v-else class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div v-if="chatAnswer" class="chat-answer">
            <div class="answer-label">AI回答：</div>
            <p>{{ chatAnswer }}</p>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTimetableStore } from '@/stores/timetable'
import { getCourses, getCourseDetail, generateAIInsights, aiChatAboutCourse } from '@/api/timetable'
import { ElMessage } from 'element-plus'

const timetableStore = useTimetableStore()
const courses = ref([])

const currentWeek = ref(10)
const selectedDay = ref(new Date().getDay() === 0 ? 6 : new Date().getDay() - 1)
const showAIInsight = ref(false)
const selectedCourse = ref(null)
const insightLoading = ref(false)
const chatQuestion = ref('')
const chatAnswer = ref('')
const chatLoading = ref(false)

const semesterLabel = computed(() => {
  return '2023-2024学年第二学期'
})

// 周几数字转中文
function getDayName(dayOfWeek) {
  const days = ['', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
  return days[dayOfWeek] || `周${dayOfWeek}`
}

const weekDays = computed(() => {
  const days = []
  const today = new Date()
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - selectedDay.value)

  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek)
    date.setDate(startOfWeek.getDate() + i)
    const isToday = date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    days.push({
      short: ['一', '二', '三', '四', '五', '六', '日'][i],
      date: date.getDate(),
      full: date.toLocaleDateString(),
      isToday
    })
  }
  return days
})

const filteredCourses = computed(() => {
  const dayOfWeek = selectedDay.value + 1
  return courses.value
    .filter(c => c.day_of_week === dayOfWeek)
    .sort((a, b) => a.start_slot - b.start_slot)
})

onMounted(async () => {
  await timetableStore.fetchCourses()
  courses.value = timetableStore.courses
})

function prevWeek() {
  if (currentWeek.value > 1) currentWeek.value--
}

function nextWeek() {
  if (currentWeek.value < 20) currentWeek.value++
}

async function showCourseDetail(course) {
  selectedCourse.value = course
  chatAnswer.value = ''
  chatQuestion.value = ''

  // 尝试获取完整的课程详情（含AI洞察）
  try {
    const res = await getCourseDetail(course.id)
    if (res.data) {
      selectedCourse.value = res.data
    }
  } catch (error) {
    console.error('Failed to fetch course detail:', error)
  }

  showAIInsight.value = true
}

async function handleGenerateInsights() {
  if (!selectedCourse.value) return

  insightLoading.value = true
  try {
    const res = await generateAIInsights(selectedCourse.value.id)
    if (res.data?.insight) {
      selectedCourse.value.ai_insight = res.data.insight
      ElMessage.success('AI学习建议已生成')
    }
  } catch (error) {
    ElMessage.error('生成失败，请稍后重试')
    console.error('Generate insights error:', error)
  } finally {
    insightLoading.value = false
  }
}

async function sendChat() {
  if (!chatQuestion.value.trim() || !selectedCourse.value) return

  chatLoading.value = true
  try {
    const res = await aiChatAboutCourse(selectedCourse.value.id, chatQuestion.value)
    if (res.data?.answer) {
      chatAnswer.value = res.data.answer
    }
  } catch (error) {
    ElMessage.error('AI回复失败，请稍后重试')
    console.error('Chat error:', error)
  } finally {
    chatLoading.value = false
  }
}

function getDifficultyType(level) {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[level] || 'info'
}

function getDifficultyLabel(level) {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[level] || level
}

function getImportanceType(level) {
  const map = { low: 'info', medium: 'warning', high: 'danger' }
  return map[level] || 'info'
}

function getImportanceLabel(level) {
  const map = { low: '低', medium: '中', high: '高' }
  return map[level] || level
}
</script>

<style scoped>
.timetable-page {
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

.import-btn {
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
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.import-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35);
}

.week-selector-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.week-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.week-label {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.week-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.day-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.day-btn:hover {
  background: #F0FDFA;
}

.day-btn.active {
  background: rgba(8, 145, 178, 0.1);
  border-color: rgba(8, 145, 178, 0.3);
}

.day-btn.isToday .day-date {
  background: #0891B2;
  color: white;
}

.day-short {
  font-size: 12px;
  color: #94A3B8;
}

.day-date {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  border-radius: 50%;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.course-item:hover {
  border-color: rgba(8, 145, 178, 0.2);
  transform: translateY(-2px);
}

.course-time-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.course-slot {
  font-size: 11px;
  color: #94A3B8;
  margin-top: 2px;
}

.course-info-col {
  flex: 1;
}

.course-info-col h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.course-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #64748B;
}

.arrow-icon {
  color: #94A3B8;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
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

.empty-state p {
  color: #64748B;
  margin-bottom: 16px;
}

.empty-action {
  display: inline-block;
  padding: 10px 20px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 10px;
  color: #0891B2;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.empty-action:hover {
  background: rgba(8, 145, 178, 0.15);
}

/* AI抽屉样式 */
.ai-drawer-content {
  padding: 0 8px;
}

.course-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.course-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.course-info-text {
  font-size: 14px;
  color: #64748B;
}

.ai-insight {
  margin-bottom: 24px;
}

.insight-section {
  margin-bottom: 20px;
}

.insight-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 10px;
}

.insight-section p {
  font-size: 14px;
  color: #475569;
  line-height: 1.7;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  position: relative;
  padding-left: 16px;
  font-size: 14px;
  color: #475569;
  line-height: 1.8;
}

.tips-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #0891B2;
}

.key-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.point-tag {
  margin: 0;
}

.insight-tags {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.generate-section {
  text-align: center;
  padding: 32px 16px;
  background: #F8FAFC;
  border-radius: 12px;
  margin-bottom: 24px;
}

.generate-hint {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 16px;
}

.generate-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-chat-section {
  border-top: 1px solid #E2E8F0;
  padding-top: 20px;
}

.ai-chat-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 12px;
}

.chat-input-wrapper {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #0891B2;
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0891B2;
  border: none;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #0E7490;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-answer {
  margin-top: 16px;
  padding: 16px;
  background: #F0FDFA;
  border-radius: 12px;
}

.answer-label {
  font-size: 12px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 8px;
}

.chat-answer p {
  font-size: 14px;
  color: #1E293B;
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>