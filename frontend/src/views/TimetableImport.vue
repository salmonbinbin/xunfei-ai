<template>
  <div class="timetable-import-page">
    <!-- 返回按钮和标题 -->
    <div class="page-header">
      <router-link to="/timetable" class="back-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </router-link>
      <div class="header-text">
        <h1 class="page-title">导入课表</h1>
        <p class="page-subtitle">上传课表文件，AI自动识别</p>
      </div>
    </div>

    <!-- 删除当前课表按钮 -->
    <div class="action-bar">
      <button class="delete-btn" @click="handleDeleteCourses">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
        删除当前课表
      </button>
    </div>

    <!-- 上传区域 -->
    <div class="upload-card">
      <h2 class="card-title">上传课表文件</h2>

      <div
        class="upload-area"
        :class="{ 'has-file': imageFile }"
        @click="triggerFileInput"
        @dragover.prevent="isDragOver = true"
        @dragleave="isDragOver = false"
        @drop.prevent="handleDrop"
      >
        <input
          type="file"
          ref="fileInput"
          accept=".pdf,image/*"
          @change="handleFileSelect"
          style="display: none"
        />

        <div v-if="!imageFile" class="upload-placeholder">
          <div class="upload-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <p class="upload-text">点击或拖拽课表文件到此处</p>
          <p class="upload-hint">支持 PDF、JPG、PNG 格式，建议使用清晰的课表截图</p>
        </div>

        <div v-else class="preview-area">
          <img v-if="imageFile?.type !== 'application/pdf'" :src="previewUrl" alt="课表预览" class="preview-image" />
          <div v-else class="pdf-preview">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <span class="pdf-name">{{ imageFile?.name }}</span>
          </div>
          <button class="remove-btn" @click.stop="removeFile">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <button
        class="recognize-btn"
        @click="startOCR"
        :disabled="!imageFile || loading"
      >
        <span v-if="loading" class="loading-content">
          <div class="loading-wrapper">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="loading-text">AI识别中...</span>
            <div class="loading-progress">
              <div class="loading-bar"></div>
            </div>
          </div>
        </span>
        <span v-else>开始识别</span>
      </button>
    </div>

    <!-- 识别结果 -->
    <div v-if="parsedCourses.length > 0" class="result-card">
      <div class="result-header">
        <h2 class="card-title">识别结果</h2>
        <span class="result-count">{{ parsedCourses.length }}节课</span>
      </div>

      <!-- 学期开始日期选择 -->
      <div class="semester-date-input">
        <label>学期开始日期：</label>
        <input
          type="date"
          v-model="semesterStartDate"
          class="date-picker"
        />
        <span class="date-hint">选择本学期第一周的周一日期</span>
      </div>

      <!-- 按星期分组显示课程 -->
      <div v-for="day in [1, 2, 3, 4, 5, 6, 7]" :key="day" class="day-section">
        <div v-if="getCoursesByDay(day).length > 0" class="day-courses">
          <h4 class="day-title">{{ getDayName(day) }}</h4>
          <div
            v-for="(course, index) in getCoursesByDay(day)"
            :key="index"
            class="course-item editable"
          >
            <div class="course-form">
              <!-- 课程名称 -->
              <div class="form-row">
                <label>课程名称：</label>
                <input
                  type="text"
                  v-model="course.name"
                  class="form-input"
                  placeholder="请输入课程名称"
                />
              </div>
              <!-- 地点和节次 -->
              <div class="form-row inline">
                <div class="form-group">
                  <label>地点：</label>
                  <input
                    type="text"
                    v-model="course.location"
                    class="form-input"
                    placeholder="如7教501"
                  />
                </div>
                <div class="form-group">
                  <label>起始节次：</label>
                  <input
                    type="number"
                    v-model.number="course.start_slot"
                    class="form-input small"
                    min="1"
                    max="12"
                  />
                </div>
                <div class="form-group">
                  <label>结束节次：</label>
                  <input
                    type="number"
                    v-model.number="course.end_slot"
                    class="form-input small"
                    min="1"
                    max="12"
                  />
                </div>
              </div>
              <!-- 周数 -->
              <div class="form-row">
                <label>上课周数：</label>
                <input
                  type="text"
                  v-model="course.week_range"
                  class="form-input"
                  placeholder="如1-16周"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加课程按钮 -->
      <button class="add-course-btn" @click="showAddCourse = !showAddCourse">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ showAddCourse ? '取消添加' : '添加课程' }}
      </button>

      <!-- 添加课程表单 -->
      <div v-if="showAddCourse" class="add-course-form">
        <h4 class="add-form-title">添加新课程</h4>
        <div class="form-row">
          <label>星期：</label>
          <select v-model="newCourse.day_of_week" class="form-input">
            <option value="1">星期一</option>
            <option value="2">星期二</option>
            <option value="3">星期三</option>
            <option value="4">星期四</option>
            <option value="5">星期五</option>
            <option value="6">星期六</option>
            <option value="7">星期日</option>
          </select>
        </div>
        <div class="form-row">
          <label>课程名称：</label>
          <input
            type="text"
            v-model="newCourse.name"
            class="form-input"
            placeholder="请输入课程名称"
          />
        </div>
        <div class="form-row inline">
          <div class="form-group">
            <label>地点：</label>
            <input
              type="text"
              v-model="newCourse.location"
              class="form-input"
              placeholder="如九教501"
            />
          </div>
          <div class="form-group">
            <label>起始节次：</label>
            <input
              type="number"
              v-model.number="newCourse.start_slot"
              class="form-input small"
              min="1"
              max="12"
            />
          </div>
          <div class="form-group">
            <label>结束节次：</label>
            <input
              type="number"
              v-model.number="newCourse.end_slot"
              class="form-input small"
              min="1"
              max="12"
            />
          </div>
        </div>
        <div class="form-row">
          <label>上课周数：</label>
          <input
            type="text"
            v-model="newCourse.week_range"
            class="form-input"
            placeholder="如1-16周"
          />
        </div>
        <div class="form-actions">
          <button class="cancel-btn" @click="showAddCourse = false">取消</button>
          <button class="confirm-btn small" @click="handleAddCourse">确认添加</button>
        </div>
      </div>

      <button class="confirm-btn" @click="confirmImport">
        确认导入
      </button>
    </div>

    <!-- 识别小技巧 -->
    <div class="tips-card">
      <h3 class="tips-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4"/>
          <path d="M12 8h.01"/>
        </svg>
        识别小技巧
      </h3>
      <ul class="tips-list">
        <li>请确保课表文件清晰，光照充足</li>
        <li>尽量使用原始课表截图或PDF，避免翻拍</li>
        <li>识别后请仔细核对课程信息</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { importTimetablePreview, importTimetableConfirm, clearAllCourses } from '@/api/timetable'

const router = useRouter()
const fileInput = ref(null)
const imageFile = ref(null)
const previewUrl = ref('')
const loading = ref(false)
const isDragOver = ref(false)
const parsedCourses = ref([])
const semesterStartDate = ref('')
const showAddCourse = ref(false)
const newCourse = ref({
  name: '',
  location: '',
  day_of_week: 1,
  start_slot: 1,
  end_slot: 1,
  week_range: '1-16周'
})

// 周几数字转中文
function getDayName(dayOfWeek) {
  const days = ['', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
  return days[dayOfWeek] || `周${dayOfWeek}`
}

// 获取默认学期开始日期（当前周的周一）
function getDefaultSemesterStart() {
  const today = new Date()
  const day = today.getDay()
  const diff = day === 0 ? -6 : 1 - day
  const monday = new Date(today)
  monday.setDate(today.getDate() + diff)
  return monday.toISOString().split('T')[0]
}

// 初始化学期开始日期
semesterStartDate.value = getDefaultSemesterStart()

// 清空现有课程
async function clearExistingCourses() {
  try {
    await ElMessageBox.confirm('导入新课表前是否清空现有课程？', '提示', {
      confirmButtonText: '清空并导入',
      cancelButtonText: '保留现有课程',
      type: 'warning'
    })
    await clearAllCourses()
    ElMessage.success('已清空现有课程')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Clear courses error:', error)
    }
  }
}

// 删除当前课表
async function handleDeleteCourses() {
  try {
    await ElMessageBox.confirm('确定要删除所有课表数据吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await clearAllCourses()
    ElMessage.success('课表已清空')
    // 清空当前识别的课程
    parsedCourses.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Delete courses error:', error)
    }
  }
}

// 添加新课程
function handleAddCourse() {
  if (!newCourse.value.name) {
    ElMessage.warning('请输入课程名称')
    return
  }

  // 添加到列表
  parsedCourses.value.push({
    name: newCourse.value.name,
    location: newCourse.value.location || null,
    day_of_week: newCourse.value.day_of_week,
    start_slot: newCourse.value.start_slot,
    end_slot: newCourse.value.end_slot,
    week_range: newCourse.value.week_range || null
  })

  // 重置表单
  newCourse.value = {
    name: '',
    location: '',
    day_of_week: 1,
    start_slot: 1,
    end_slot: 1,
    week_range: '1-16周'
  }
  showAddCourse.value = false
  ElMessage.success('已添加课程')
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    setImageFile(file)
  }
}

function handleDrop(event) {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && (file.type.startsWith('image/') || file.type === 'application/pdf')) {
    setImageFile(file)
  }
}

function setImageFile(file) {
  imageFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function removeFile() {
  imageFile.value = null
  previewUrl.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function startOCR() {
  if (!imageFile.value) return

  loading.value = true
  try {
    // 使用星火图片理解API
    const res = await importTimetablePreview(imageFile.value)
    console.log('识别结果:', res)

    // axios 响应数据在 res.data 中
    const data = res.data

    // 根据success字段判断识别是否成功
    if (data.success && data.courses && data.courses.length > 0) {
      parsedCourses.value = data.courses
      ElMessage.success(data.message || '识别完成，请确认导入')
    } else if (data.success && data.courses && data.courses.length === 0) {
      // 识别成功但没有课程
      ElMessage.warning('未能识别出课程，请上传清晰的课表图片')
      parsedCourses.value = []
    } else if (data.raw_text) {
      // 有原始文本但解析失败
      ElMessage.warning('识别结果格式异常，请手动确认')
      parsedCourses.value = []
    } else {
      ElMessage.error(data.message || '识别失败，请重试')
      parsedCourses.value = []
    }
  } catch (error) {
    ElMessage.error('识别失败')
    console.error('OCR error:', error)
  } finally {
    loading.value = false
  }
}

// 按星期几筛选课程
function getCoursesByDay(dayOfWeek) {
  return parsedCourses.value.filter(course => course.day_of_week === dayOfWeek)
}

async function confirmImport() {
  if (parsedCourses.value.length === 0) {
    ElMessage.warning('没有可导入的课程')
    return
  }

  loading.value = true
  try {
    await importTimetableConfirm(parsedCourses.value, semesterStartDate.value)
    ElMessage.success('课表导入成功')
    router.push('/timetable')
  } catch (error) {
    ElMessage.error('导入失败')
    console.error('Confirm error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.timetable-import-page {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
  background: #F8FAFC;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.delete-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #FFFFFF;
  border: 1px solid #EF4444;
  border-radius: 8px;
  color: #EF4444;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background: #FEF2F2;
  border-color: #DC2626;
  color: #DC2626;
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
  background: #F0FDFA;
  border-color: #0891B2;
  color: #0891B2;
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

.upload-card,
.result-card,
.tips-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 16px;
}

.upload-area {
  border: 2px dashed #E2E8F0;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.upload-area:hover {
  border-color: #0891B2;
  background: #F0FDFA;
}

.upload-area.has-file {
  padding: 16px;
  border-style: solid;
  border-color: rgba(8, 145, 178, 0.3);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  width: 72px;
  height: 72px;
  background: rgba(8, 145, 178, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: #94A3B8;
}

.preview-area {
  position: relative;
  display: inline-block;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
}

.pdf-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #64748B;
}

.pdf-name {
  font-size: 14px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 28px;
  height: 28px;
  background: rgba(220, 38, 38, 0.9);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recognize-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.recognize-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35);
}

.recognize-btn:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(1) { animation-delay: 0s; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1.2); opacity: 1; }
}

.loading-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.loading-progress {
  width: 120px;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.loading-bar {
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 2px;
  animation: loading 2s ease-in-out infinite;
}

@keyframes loading {
  0% { width: 0%; margin-left: 0; }
  50% { width: 60%; margin-left: 20%; }
  100% { width: 0%; margin-left: 100%; }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-count {
  padding: 4px 12px;
  background: rgba(8, 145, 178, 0.1);
  border-radius: 20px;
  color: #0891B2;
  font-size: 13px;
  font-weight: 500;
}

.semester-date-input {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background: rgba(8, 145, 178, 0.05);
  border-radius: 12px;
}

.semester-date-input label {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
}

.date-picker {
  padding: 8px 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  color: #1E293B;
  background: #FFFFFF;
}

.date-picker:focus {
  outline: none;
  border-color: #0891B2;
}

.date-hint {
  font-size: 12px;
  color: #94A3B8;
}

.day-section {
  margin-bottom: 16px;
}

.day-title {
  font-size: 14px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 8px;
  padding-left: 8px;
  border-left: 3px solid #0891B2;
}

.day-courses {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.course-item {
  padding: 14px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
}

.course-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.course-teacher {
  font-size: 13px;
  color: #64748B;
  margin-bottom: 8px;
}

.course-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #94A3B8;
}

.detail-tag {
  padding: 2px 8px;
  background: rgba(8, 145, 178, 0.08);
  border-radius: 4px;
}

.location {
  background: rgba(5, 150, 105, 0.08);
  color: #059669;
}

/* 编辑表单样式 */
.course-item.editable {
  padding: 0;
  background: #FFFFFF;
}

.course-form {
  padding: 16px;
}

.form-row {
  margin-bottom: 12px;
}

.form-row.inline {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 80px;
}

.form-row label {
  display: block;
  font-size: 12px;
  color: #64748B;
  margin-bottom: 4px;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  color: #1E293B;
  background: #F8FAFC;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #0891B2;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
}

.form-input.small {
  width: 60px;
  text-align: center;
}

.form-row.inline .form-group {
  display: flex;
  flex-direction: column;
}

.add-course-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  background: #FFFFFF;
  border: 2px dashed #E2E8F0;
  border-radius: 12px;
  color: #0891B2;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-course-btn:hover {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.05);
}

.add-course-form {
  margin-top: 16px;
  padding: 16px;
  background: #F0FDFA;
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 12px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.cancel-btn {
  flex: 1;
  padding: 10px 24px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  color: #64748B;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
  color: #475569;
}

.add-form-title {
  font-size: 14px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 12px;
}

.confirm-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #059669, #10B981);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.35);
}

.confirm-btn.small {
  flex: 1;
  padding: 10px 24px;
  font-size: 14px;
}

.tips-card {
  background: rgba(8, 145, 178, 0.05);
  border-color: rgba(8, 145, 178, 0.15);
}

.tips-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 12px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  position: relative;
  padding-left: 16px;
  font-size: 13px;
  color: #64748B;
  line-height: 1.8;
}

.tips-list li::before {
  content: '·';
  position: absolute;
  left: 0;
  color: #0891B2;
}
</style>
