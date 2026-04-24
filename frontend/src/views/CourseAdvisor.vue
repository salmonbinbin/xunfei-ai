<template>
  <div class="course-advisor-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <router-link to="/" class="back-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </router-link>
      <div class="header-text">
        <h1 class="page-title">智能选课助手</h1>
        <p class="page-subtitle">AI帮你找到最合适的课程</p>
      </div>
      <div class="semester-select">
        <el-select v-model="currentSemester" size="default" @change="onSemesterChange">
          <el-option label="2024-2025学年 第一学期" value="2024-1"/>
          <el-option label="2023-2024学年 第二学期" value="2023-2"/>
          <el-option label="2023-2024学年 第一学期" value="2023-1"/>
        </el-select>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧边栏 - 学生画像 -->
      <aside class="sidebar">
        <div class="sidebar-card profile-card">
          <StudentRadar
            :radar-data="store.radarData"
            :ability-type="selectedAbilityType"
            :profile-data="{
              major: store.profile.major,
              grade: store.profile.grade,
              goal: store.profile.goal
            }"
            @update:abilityType="onAbilityTypeChange"
          />
        </div>

        <div class="sidebar-card chat-card">
          <AIChatPanel
            :messages="store.chatHistory"
            :recommended-courses="store.suggestedCourses"
            :loading="store.loading.chat"
            @send="onChatSend"
            @select-course="onCourseSelect"
          />
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 标签导航 -->
        <div class="tab-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: currentTab === tab.key }"
            @click="onTabChange(tab.key)"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- 选课时间表 -->
        <div v-if="store.selectedCourseIds.length > 0" class="timeline-section">
          <ScheduleTimeline
            :selected-courses="selectedCourseDetails"
            :conflicts="currentConflicts"
          />
        </div>

        <!-- 推荐课程列表 -->
        <div class="courses-section">
          <div v-if="store.loading.recommendations" class="loading-state">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>

          <div v-else-if="store.recommendedCourses.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#CBD5E1" stroke-width="1.5">
              <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
            <p>点击"智能推荐"获取选课建议</p>
          </div>

          <div v-else class="course-list">
            <CourseCard
              v-for="course in store.recommendedCourses"
              :key="course.id"
              :course="course"
              :is-selected="store.selectedCourseIds.includes(course.id)"
              @toggle-select="onToggleCourseSelect"
              @show-detail="onShowCourseDetail"
              @show-reason="onShowCourseReason"
            />
          </div>

          <!-- 分页 -->
          <div v-if="store.pagination.totalPages > 1" class="pagination">
            <button
              class="page-btn"
              :disabled="store.pagination.page <= 1"
              @click="onPageChange(store.pagination.page - 1)"
            >
              上一页
            </button>
            <span class="page-info">
              第 {{ store.pagination.page }} / {{ store.pagination.totalPages }} 页
              （共 {{ store.pagination.total }} 门课程）
            </span>
            <button
              class="page-btn"
              :disabled="store.pagination.page >= store.pagination.totalPages"
              @click="onPageChange(store.pagination.page + 1)"
            >
              下一页
            </button>
          </div>
        </div>

        <!-- 已选课程确认区 -->
        <div v-if="store.selectedCourseIds.length > 0" class="selection-footer">
          <div class="selection-info">
            <span class="selection-count">已选 {{ store.selectedCourseIds.length }} 门课程</span>
            <span class="selection-credits">{{ selectedTotalCredits }} 学分</span>
          </div>
          <div class="selection-actions">
            <button class="action-btn clear-btn" @click="clearSelection">清空</button>
            <button class="action-btn submit-btn" @click="submitSelection">确认选课</button>
          </div>
        </div>
      </main>
    </div>

    <!-- 课程详情弹窗 -->
    <el-dialog v-model="showCourseDetail" title="课程详情" width="500px" class="course-detail-dialog">
      <div v-if="selectedCourse" class="course-detail-content">
        <div class="detail-header">
          <h3>{{ selectedCourse.name }}</h3>
          <div class="detail-rating">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="#D97706">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span>{{ selectedCourse.rating }}</span>
          </div>
        </div>

        <div class="detail-info">
          <div class="info-item">
            <span class="info-label">授课教师</span>
            <span class="info-value">{{ selectedCourse.teacher }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">学分</span>
            <span class="info-value">{{ selectedCourse.credits }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">上课时间</span>
            <span class="info-value">{{ formatSchedule(selectedCourse) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">上课地点</span>
            <span class="info-value">{{ selectedCourse.location || '待定' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">已选/容量</span>
            <span class="info-value">{{ selectedCourse.enrolled }}/{{ selectedCourse.capacity }}</span>
          </div>
        </div>

        <div v-if="selectedCourse.description" class="detail-desc">
          <h4>课程简介</h4>
          <p>{{ selectedCourse.description }}</p>
        </div>

        <div v-if="courseDetailData?.prerequisites?.length" class="detail-prerequisites">
          <h4>先修课程</h4>
          <div class="prerequisite-list">
            <span
              v-for="p in courseDetailData.prerequisites"
              :key="p.id"
              class="prerequisite-item"
              :class="{ completed: p.status === 'completed' }"
            >
              {{ p.name }}
            </span>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 推荐理由弹窗 -->
    <el-dialog v-model="showCourseReason" title="推荐理由" width="450px" class="reason-dialog">
      <div v-if="selectedCourse" class="reason-content">
        <div class="reason-header">
          <h3>{{ selectedCourse.name }}</h3>
        </div>
        <div class="reason-body">
          <p>{{ selectedCourse.match_reason || '这门课程与您的学习目标和能力偏好相匹配。' }}</p>
        </div>
        <div class="reason-tags">
          <span v-for="tag in selectedCourse.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseAdvisorStore } from '@/stores/courseAdvisor'
import StudentRadar from '@/components/course-advisor/StudentRadar.vue'
import CourseCard from '@/components/course-advisor/CourseCard.vue'
import ScheduleTimeline from '@/components/course-advisor/ScheduleTimeline.vue'
import AIChatPanel from '@/components/course-advisor/AIChatPanel.vue'

const store = useCourseAdvisorStore()

const selectedAbilityType = ref('逻辑型')

const currentSemester = ref('2024-1')
const currentTab = ref('recommend')
const showCourseDetail = ref(false)
const showCourseReason = ref(false)
const selectedCourse = ref(null)
const courseDetailData = ref(null)

const tabs = [
  { key: 'recommend', label: 'AI智能推荐', icon: '✨' },
  { key: 'mandatory', label: '必修课程', icon: '📚' },
  { key: 'elective', label: '选修课程', icon: '🎯' },
  { key: 'cross_major', label: '跨专业选修', icon: '🌐' },
  { key: 'my_selected', label: '我的已选', icon: '📋' }
]

const selectedCourseDetails = computed(() =>
  store.recommendedCourses.filter(c => store.selectedCourseIds.includes(c.id))
)

const selectedTotalCredits = computed(() =>
  selectedCourseDetails.value.reduce((sum, c) => sum + (c.credits || 0), 0)
)

const currentConflicts = computed(() => store.detectConflicts())

onMounted(async () => {
  await store.fetchProfile()
  // 获取已选课程（用于雷达图动态计算）
  await store.fetchMySelectedCourses()
  // 默认加载AI智能推荐
  await store.fetchRecommendations('all')
})

function onAbilityTypeChange(type) {
  selectedAbilityType.value = type
}

function onSemesterChange(semester) {
  store.setSemester(semester)
  store.fetchRecommendations(currentTab.value === 'recommend' ? 'all' : currentTab.value, null, 1)
}

async function onTabChange(tab) {
  currentTab.value = tab
  if (tab === 'my_selected') {
    // 我的已选 - 从store获取已选课程
    await store.fetchMySelectedCourses()
    return
  }
  const categoryMap = {
    recommend: 'all',
    mandatory: 'mandatory',
    elective: 'elective',
    cross_major: 'cross_major'
  }
  await store.fetchRecommendations(categoryMap[tab])
}

async function onPageChange(page) {
  await store.fetchRecommendations(currentTab.value === 'recommend' ? 'all' : currentTab.value, null, page)
}

function onToggleCourseSelect(courseId) {
  store.toggleCourseSelection(courseId)
}

function onShowCourseDetail(course) {
  selectedCourse.value = course
  courseDetailData.value = store.fetchCourseDetail(course.id)
  showCourseDetail.value = true
}

function onShowCourseReason(course) {
  selectedCourse.value = course
  showCourseReason.value = true
}

async function onChatSend(message) {
  await store.sendChat(message)
}

async function onCourseSelect(course) {
  // 先尝试在当前推荐列表中查找匹配课程
  let matchedCourse = store.recommendedCourses.find(c => c.name === course.name)

  if (matchedCourse) {
    // 使用匹配课程的ID进行选择
    store.toggleCourseSelection(matchedCourse.id)
    return
  }

  // 从已选课程中查找
  matchedCourse = store.mySelectedCourses.find(c => c.name === course.name)
  if (matchedCourse) {
    store.toggleCourseSelection(matchedCourse.id)
    return
  }

  // 尝试通过API根据课程名称搜索课程目录获取完整信息
  try {
    const response = await store.searchCourseByName(course.name)
    if (response && response.data && response.data.success) {
      const catalogCourse = response.data.course
      if (catalogCourse) {
        // 添加到推荐列表
        store.recommendedCourses.push({
          ...catalogCourse,
          match_reason: course.match_reason || '',
          conflict_status: 'none'
        })
        // 选课
        store.toggleCourseSelection(catalogCourse.id)
        return
      }
    }
  } catch (e) {
    console.warn('[CourseAdvisor] 无法找到课程:', course.name)
  }

  // 如果还是找不到，使用课程名称作为临时选择（用于显示）
  if (course.name) {
    ElMessage.warning(`课程"${course.name}"不在课程目录中，无法选课`)
  }
}

function clearSelection() {
  store.selectedCourseIds.splice(0, store.selectedCourseIds.length)
}

async function submitSelection() {
  const result = await store.submitSelection()
  if (result) {
    ElMessage.success('选课方案已保存')
    if (result.conflicts?.length > 0) {
      ElMessage.warning(`检测到 ${result.conflicts.length} 个时间冲突`)
    }
    store.selectedCourseIds.splice(0, store.selectedCourseIds.length)
  }
}

function formatSchedule(course) {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const day = days[course.day_of_week] || '未知'
  return `${day} ${course.start_slot}-${course.end_slot}节`
}
</script>

<style scoped>
.course-advisor-page {
  min-height: 100vh;
  background: #F8FAFC;
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.back-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  color: #64748B;
  text-decoration: none;
  transition: all 0.2s ease;
}

.back-btn:hover {
  border-color: #0891B2;
  color: #0891B2;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 2px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
}

.semester-select {
  width: 200px;
}

.main-content {
  display: flex;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.profile-card {
  padding: 0;
  overflow: hidden;
}

.chat-card {
  overflow: hidden;
}

.content-area {
  flex: 1;
  min-width: 0;
}

.tab-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background: #FFFFFF;
  padding: 8px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  color: #fff;
}

.tab-btn:not(.active):hover {
  background: #F1F5F9;
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  font-size: 14px;
  font-weight: 500;
}

.timeline-section {
  margin-bottom: 20px;
}

.courses-section {
  min-height: 300px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748B;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(8, 145, 178, 0.2);
  border-top-color: #0891B2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94A3B8;
}

.empty-state p {
  margin-top: 16px;
  font-size: 14px;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
  margin-top: 8px;
}

.page-btn {
  padding: 8px 16px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #F1F5F9;
  border-color: #0891B2;
  color: #0891B2;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #64748B;
}

.selection-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  margin-top: 20px;
}

.selection-info {
  display: flex;
  gap: 16px;
}

.selection-count {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.selection-credits {
  font-size: 14px;
  color: #0891B2;
  font-weight: 500;
}

.selection-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn {
  background: #F1F5F9;
  border: 1px solid #E2E8F0;
  color: #64748B;
}

.clear-btn:hover {
  background: #E2E8F0;
  color: #475569;
}

.submit-btn {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  color: #fff;
}

.submit-btn:hover {
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
  transform: translateY(-1px);
}

/* 弹窗样式 */
.course-detail-content {
  padding: 8px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #D97706;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  background: #F8FAFC;
  border-radius: 8px;
}

.info-label {
  font-size: 13px;
  color: #64748B;
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: #1E293B;
}

.detail-desc h4,
.detail-prerequisites h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 10px;
}

.detail-desc p {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

.prerequisite-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.prerequisite-item {
  padding: 4px 12px;
  background: #F1F5F9;
  border-radius: 16px;
  font-size: 12px;
  color: #64748B;
}

.prerequisite-item.completed {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.reason-content {
  padding: 8px;
}

.reason-header {
  margin-bottom: 16px;
}

.reason-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.reason-body {
  padding: 16px;
  background: #F8FAFC;
  border-radius: 12px;
  margin-bottom: 16px;
}

.reason-body p {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
}

.reason-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 12px;
  font-size: 12px;
  color: #0891B2;
}
</style>

<style>
/* 全局覆盖 */
.course-detail-dialog .el-dialog {
  border-radius: 16px;
}

.course-detail-dialog .el-dialog__header {
  padding: 16px 20px;
  border-bottom: 1px solid #F1F5F9;
}

.reason-dialog .el-dialog {
  border-radius: 16px;
}

.reason-dialog .el-dialog__header {
  padding: 16px 20px;
  border-bottom: 1px solid #F1F5F9;
}

.el-select {
  --el-select-input-focus-border-color: #0891B2;
}
</style>