<template>
  <div class="review-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">录音回顾</h1>
        <p class="page-subtitle">记录课堂内容，AI智能总结</p>
      </div>
      <el-button type="primary" class="upload-btn" @click="showUploadDialog = true">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        上传录音
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(8, 145, 178, 0.1);">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          </svg>
        </div>
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总录音数</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(5, 150, 105, 0.1);">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="stat-value">{{ stats.duration }}</div>
        <div class="stat-label">总时长(分钟)</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(139, 92, 246, 0.1);">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <div class="stat-value">{{ stats.exports }}</div>
        <div class="stat-label">导出次数</div>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        :class="['tab-btn', { active: activeTab === tab.value }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 录音列表 -->
    <div v-loading="loading" class="recordings-list">
      <router-link
        v-for="item in filteredList"
        :key="item.id"
        :to="`/review/${item.id}`"
        class="recording-item"
      >
        <div class="recording-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
          </svg>
        </div>
        <div class="recording-content">
          <div class="recording-header">
            <h3>{{ item.title || '未命名录音' }}</h3>
            <span :class="['status-badge', item.status]">
              {{ statusLabelMap[item.status] || item.status }}
            </span>
            <button class="delete-btn" @click="(e) => handleDelete(item, e)" title="删除">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
          <p class="recording-meta">
            {{ formatDate(item.created_at) }} · {{ formatDuration(item.duration) }}
            <span v-if="item.record_type" class="type-tag">
              {{ item.record_type === 'course' ? '课程' : '会议' }}
            </span>
          </p>
          <p v-if="item.summary" class="recording-summary">{{ item.summary }}</p>
        </div>
        <svg class="arrow-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </router-link>

      <div v-if="!loading && filteredList.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="1.5">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
          </svg>
        </div>
        <p>暂无录音记录</p>
        <el-button type="primary" @click="showUploadDialog = true">上传第一个录音</el-button>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传录音"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="upload-form">
        <el-form :model="uploadForm" label-position="top">
          <el-form-item label="录音类型">
            <el-radio-group v-model="uploadForm.record_type">
              <el-radio value="course">课程</el-radio>
              <el-radio value="meeting">会议</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="语言">
            <el-select v-model="uploadForm.language" style="width: 100%">
              <el-option value="mandarin" label="普通话" />
              <el-option value="cantonese" label="粤语" />
              <el-option value="english" label="英语" />
            </el-select>
          </el-form-item>

          <el-form-item label="标题（可选）">
            <el-input v-model="uploadForm.title" placeholder="为录音添加一个标题" />
          </el-form-item>

          <el-form-item label="音频文件">
            <el-upload
              ref="uploadRef"
              class="audio-upload"
              drag
              :auto-upload="false"
              :limit="1"
              :file-list="fileList"
              :before-upload="beforeUpload"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              accept=".mp3,.wav,audio/mp3,audio/wav"
            >
              <div class="upload-content">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="1.5">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                </svg>
                <p class="upload-text">将音频文件拖到此处，或<span class="upload-link">点击上传</span></p>
                <p class="upload-hint">支持MP3/WAV格式，文件大小不超过50MB</p>
              </div>
            </el-upload>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelUpload">取消</el-button>
          <el-button
            type="primary"
            :loading="uploading"
            :disabled="!uploadForm.audio"
            @click="handleUpload"
          >
            {{ uploading ? `上传中 ${uploadProgress}%` : '开始上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useAsync } from '@/utils/useAsync'
import { getReviewList, uploadAudio as uploadAudioApi, deleteReview as deleteReviewApi } from '@/api/review'
import { formatDate, formatDuration } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('all')

const tabs = [
  { label: '全部', value: 'all' },
  { label: '已完成', value: 'completed' },
  { label: '处理中', value: 'processing' },
  { label: '待处理', value: 'pending' },
  { label: '失败', value: 'failed' }
]

const statusLabelMap = {
  pending: '待处理',
  processing: '处理中',
  completed: '已完成',
  failed: '失败'
}

// 计算统计数据
const stats = computed(() => {
  if (!reviewList.value || reviewList.value.length === 0) {
    return { total: 0, duration: 0, exports: 0 }
  }

  const completedList = reviewList.value.filter(r => r.status === 'completed')

  return {
    total: reviewList.value.length,
    duration: Math.round(reviewList.value.reduce((sum, r) => sum + (r.duration || 0), 0) / 60), // 转换为分钟
    exports: completedList.length // 导出次数用已完成数量代替
  }
})

const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadRef = ref(null)
const fileList = ref([])

const uploadForm = ref({
  record_type: 'course',
  language: 'mandarin',
  title: '',
  audio: null
})

// 获取录音列表
const { data: reviewList, loading, execute: fetchReviewList } = useAsync(
  () => getReviewList().then(res => res.data),
  { immediate: true }
)

const filteredList = computed(() => {
  if (!reviewList.value) return []
  if (activeTab.value === 'all') return reviewList.value

  const statusMap = {
    completed: ['completed'],
    processing: ['processing'],
    pending: ['pending'],
    failed: ['failed']
  }
  const validStatuses = statusMap[activeTab.value] || []
  return reviewList.value.filter(r => validStatuses.includes(r.status))
})

// 自动刷新列表（当有待处理的录音时）
onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// 自动刷新定时器
let pollingTimer = null

function startPolling() {
  stopPolling()
  pollingTimer = setInterval(() => {
    // 检查是否有正在处理的录音
    const hasProcessing = reviewList.value?.some(r => r.status === 'processing' || r.status === 'transcribed')
    if (hasProcessing) {
      fetchReviewList()
    } else {
      stopPolling()
    }
  }, 3000)
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 上传相关
function beforeUpload(file) {
  const isAudio = file.type === 'audio/mp3' || file.type === 'audio/wav' ||
                  file.name.endsWith('.mp3') || file.name.endsWith('.wav')
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isAudio) {
    ElMessage.error('只能上传MP3或WAV格式的音频文件')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB')
    return false
  }
  return true
}

function handleFileChange(file, files) {
  fileList.value = files
  uploadForm.value.audio = file.raw
}

function handleFileRemove() {
  fileList.value = []
  uploadForm.value.audio = null
}

async function handleUpload() {
  if (!uploadForm.value.audio) {
    ElMessage.warning('请选择要上传的音频文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  try {
    await uploadAudioApi(uploadForm.value.audio, {
      record_type: uploadForm.value.record_type,
      language: uploadForm.value.language,
      title: uploadForm.value.title,
      onProgress: (percent) => {
        uploadProgress.value = percent
      }
    })

    ElMessage.success('上传成功，正在转写中...')
    cancelUpload()
    fetchReviewList()
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

function cancelUpload() {
  showUploadDialog.value = false
  uploadForm.value = {
    record_type: 'course',
    language: 'mandarin',
    title: '',
    audio: null
  }
  fileList.value = []
  uploadRef.value?.clearFiles()
}

// 删除录音
async function handleDelete(item, event) {
  event.preventDefault()
  event.stopPropagation()

  try {
    await ElMessageBox.confirm(
      `确定要删除录音"${item.title || '未命名录音'}"吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteReviewApi(item.id)
    ElMessage.success('删除成功')
    fetchReviewList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
    }
  }
}
</script>

<style scoped>
.review-page {
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

.upload-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  padding: 10px 18px;
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(8, 145, 178, 0.35);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-card:hover {
  border-color: rgba(8, 145, 178, 0.2);
}

.stat-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #64748B;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  color: #64748B;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  border-color: rgba(8, 145, 178, 0.3);
  color: #0891B2;
}

.tab-btn.active {
  background: rgba(8, 145, 178, 0.1);
  border-color: rgba(8, 145, 178, 0.3);
  color: #0891B2;
}

.recordings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recording-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.recording-item:hover {
  border-color: rgba(8, 145, 178, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.recording-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(8, 145, 178, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
  flex-shrink: 0;
}

.recording-content {
  flex: 1;
  min-width: 0;
}

.recording-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.recording-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.completed {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.status-badge.processing {
  background: rgba(8, 145, 178, 0.1);
  color: #0891B2;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.delete-btn {
  margin-left: auto;
  padding: 4px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #94A3B8;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.recording-meta {
  font-size: 13px;
  color: #94A3B8;
  margin-bottom: 6px;
}

.type-tag {
  margin-left: 8px;
  padding: 2px 8px;
  background: rgba(8, 145, 178, 0.08);
  border-radius: 8px;
  color: #0891B2;
  font-size: 11px;
}

.recording-summary {
  font-size: 13px;
  color: #64748B;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.upload-form {
  padding: 10px 0;
}

.audio-upload {
  width: 100%;
}

.upload-content {
  padding: 30px 20px;
  text-align: center;
}

.upload-content svg {
  margin-bottom: 12px;
}

.upload-text {
  font-size: 14px;
  color: #475569;
  margin-bottom: 8px;
}

.upload-link {
  color: #0891B2;
  cursor: pointer;
}

.upload-hint {
  font-size: 12px;
  color: #94A3B8;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

<style>
.el-upload-dragger {
  background: #F8FAFC;
  border: 1px dashed #E2E8F0;
  border-radius: 12px;
}

.el-upload-dragger:hover {
  border-color: #0891B2;
}
</style>