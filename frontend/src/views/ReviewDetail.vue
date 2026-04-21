<template>
  <div class="review-detail-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <router-link to="/review" class="back-btn">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </router-link>
      <div class="header-text">
        <h1 class="page-title">{{ detail?.title || '录音详情' }}</h1>
        <p class="page-subtitle">{{ formatDate(detail?.created_at) }}</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="loading-spinner" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 内容区域 -->
    <template v-else-if="detail">
      <!-- 音频播放器 -->
      <div class="player-card">
        <button class="play-btn" :class="{ playing: isPlaying }" @click="togglePlay">
          <svg v-if="!isPlaying" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
        </button>
        <div class="progress-area">
          <div class="progress-bar" @click="seekTo">
            <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
          </div>
          <div class="progress-time">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>

      <!-- 信息卡片 -->
      <div class="info-card">
        <div class="info-item">
          <span class="info-label">类型</span>
          <span class="info-value">{{ detail.record_type === 'course' ? '课程' : '会议' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">时长</span>
          <span class="info-value">{{ formatDuration(detail.duration) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">状态</span>
          <span :class="['status-badge', detail.status]">
            {{ statusLabelMap[detail.status] || detail.status }}
          </span>
        </div>
      </div>

      <!-- 转写文本 -->
      <div class="content-card" v-if="detail.transcription">
        <div class="card-header">
          <h2 class="card-title">转写文本</h2>
          <button class="copy-btn" @click="copyText(detail.transcription.raw_text)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            复制全文
          </button>
        </div>
        <div class="transcript-text">{{ detail.transcription.raw_text }}</div>
      </div>

      <!-- 转写中状态 -->
      <div class="content-card processing-card" v-else-if="detail.status === 'processing'">
        <div class="processing-indicator">
          <el-icon class="loading-spinner"><Loading /></el-icon>
          <span>正在转写，请稍候...</span>
        </div>
      </div>

      <!-- AI摘要 -->
      <div class="content-card" v-if="detail.summary">
        <div class="card-header">
          <h2 class="card-title">AI摘要</h2>
          <button class="copy-btn" @click="handleRegenerate" :disabled="regenerating">
            <el-icon v-if="regenerating" class="loading-spinner"><Loading /></el-icon>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 2v6h-6"/>
              <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
              <path d="M3 22v-6h6"/>
              <path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
            {{ regenerating ? '重新生成中...' : '重新生成' }}
          </button>
        </div>
        <div class="summary-content">
          <template v-if="detail.record_type === 'course'">
            <div class="summary-section" v-if="detail.summary.topic">
              <h3 class="summary-section-title">主题</h3>
              <p class="summary-section-text">{{ detail.summary.topic }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.key_points">
              <h3 class="summary-section-title">核心知识点</h3>
              <p class="summary-section-text">{{ detail.summary.key_points }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.difficulties">
              <h3 class="summary-section-title">重点难点</h3>
              <p class="summary-section-text">{{ detail.summary.difficulties }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.memorable_quote">
              <h3 class="summary-section-title">金句</h3>
              <p class="summary-section-text memorable-quote">"{{ detail.summary.memorable_quote }}"</p>
            </div>
            <div class="summary-section" v-if="detail.summary.next_suggestion">
              <h3 class="summary-section-title">预习建议</h3>
              <p class="summary-section-text">{{ detail.summary.next_suggestion }}</p>
            </div>
          </template>
          <template v-else>
            <div class="summary-section" v-if="detail.summary.topic">
              <h3 class="summary-section-title">会议主题</h3>
              <p class="summary-section-text">{{ detail.summary.topic }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.key_points">
              <h3 class="summary-section-title">讨论要点</h3>
              <p class="summary-section-text">{{ detail.summary.key_points }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.difficulties">
              <h3 class="summary-section-title">决议事项</h3>
              <p class="summary-section-text">{{ detail.summary.difficulties }}</p>
            </div>
            <div class="summary-section" v-if="detail.summary.next_suggestion">
              <h3 class="summary-section-title">待办事项</h3>
              <p class="summary-section-text">{{ detail.summary.next_suggestion }}</p>
            </div>
          </template>
        </div>
      </div>

      <!-- 摘要生成中 -->
      <div class="content-card processing-card" v-else-if="detail.status === 'transcribed'">
        <div class="processing-indicator">
          <el-icon class="loading-spinner"><Loading /></el-icon>
          <span>正在生成AI摘要...</span>
        </div>
      </div>

      <!-- 导出操作 -->
      <div class="export-card" v-if="detail.status === 'completed'">
        <h2 class="card-title">导出</h2>
        <div class="export-buttons">
          <button class="export-btn" :class="{ loading: exportingDocx }" @click="handleExportDocx">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            <span v-if="exportingDocx">导出中...</span>
            <span v-else>导出Word</span>
          </button>
          <button class="export-btn" :class="{ loading: exportingPptx }" @click="handleExportPptx">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span v-if="exportingPptx">导出中...</span>
            <span v-else>导出PPT</span>
          </button>
        </div>
      </div>
    </template>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      <p>加载失败，请重试</p>
      <el-button type="primary" @click="fetchDetail">重新加载</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAsync } from '@/utils/useAsync'
import { getReviewDetail, exportToDocx, exportToPptx, downloadFile, regenerateSummary } from '@/api/review'
import { formatDate, formatDuration } from '@/utils/format'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const reviewId = route.params.id

const statusLabelMap = {
  pending: '待处理',
  processing: '处理中',
  transcribed: '已转写',
  completed: '已完成'
}

// 获取详情
const { data: detail, loading, error, execute: fetchDetail } = useAsync(
  () => getReviewDetail(reviewId).then(res => res.data),
  { immediate: false }
)

// 音频播放
const audio = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)

onMounted(() => {
  fetchDetail()
  // 当状态为处理中时，每3秒自动刷新一次
  startPolling()
})

onUnmounted(() => {
  stopPolling()
  if (audio.value) {
    audio.value.pause()
    audio.value = null
  }
})

// 自动刷新定时器
let pollingTimer = null

function startPolling() {
  stopPolling()
  pollingTimer = setInterval(() => {
    // 只有在处理中或转写状态下才自动刷新
    if (detail.value && (detail.value.status === 'processing' || detail.value.status === 'transcribed')) {
      fetchDetail()
    } else {
      // 已完成或失败，停止轮询
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

function togglePlay() {
  if (!audio.value) {
    if (detail.value?.audio_url) {
      // 拼接完整的API URL
      const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
      const audioUrl = detail.value.audio_url.startsWith('http')
        ? detail.value.audio_url
        : `${apiBase}${detail.value.audio_url}`
      audio.value = new Audio(audioUrl)
      audio.value.addEventListener('timeupdate', updateProgress)
      audio.value.addEventListener('loadedmetadata', () => {
        duration.value = audio.value.duration
      })
      audio.value.addEventListener('ended', () => {
        isPlaying.value = false
        currentTime.value = 0
        progress.value = 0
      })
    }
  }

  if (audio.value) {
    if (isPlaying.value) {
      audio.value.pause()
    } else {
      audio.value.play()
    }
    isPlaying.value = !isPlaying.value
  }
}

function updateProgress() {
  if (audio.value) {
    currentTime.value = audio.value.currentTime
    progress.value = (currentTime.value / duration.value) * 100
  }
}

function seekTo(event) {
  if (audio.value && duration.value > 0) {
    const rect = event.currentTarget.getBoundingClientRect()
    const percent = (event.clientX - rect.left) / rect.width
    audio.value.currentTime = percent * duration.value
  }
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 复制文本
async function copyText(text) {
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 重新生成AI摘要
const regenerating = ref(false)

async function handleRegenerate() {
  if (regenerating.value) return
  if (!detail.value?.id) {
    ElMessage.error('录音信息不存在')
    return
  }

  regenerating.value = true
  try {
    ElMessage.info('正在重新生成摘要，请稍候...')
    await regenerateSummary(detail.value.id)
    ElMessage.success('摘要重新生成成功')

    // 重新加载详情
    await fetchDetail()
  } catch (err) {
    console.error('Regenerate summary failed:', err)
    ElMessage.error(err.message || '重新生成失败，请稍后重试')
  } finally {
    regenerating.value = false
  }
}

// 导出
const exportingDocx = ref(false)
const exportingPptx = ref(false)

async function handleExportDocx() {
  if (exportingDocx.value) return
  if (!detail.value?.summary?.id) {
    ElMessage.error('请等待总结生成完成')
    return
  }
  exportingDocx.value = true

  try {
    const response = await exportToDocx(detail.value.summary.id)
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    const filename = `${detail.value?.title || '录音回顾'}_${Date.now()}.docx`
    downloadFile(blob, filename)
    ElMessage.success('DOCX导出成功')
  } catch (err) {
    console.error('Export DOCX failed:', err)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exportingDocx.value = false
  }
}

async function handleExportPptx() {
  if (exportingPptx.value) return
  if (!detail.value?.summary?.id) {
    ElMessage.error('请等待总结生成完成')
    return
  }
  exportingPptx.value = true

  try {
    const response = await exportToPptx(detail.value.summary.id)
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' })
    const filename = `${detail.value?.title || '录音回顾'}_${Date.now()}.pptx`
    downloadFile(blob, filename)
    ElMessage.success('PPTX导出成功')
  } catch (err) {
    console.error('Export PPTX failed:', err)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exportingPptx.value = false
  }
}
</script>

<style scoped>
.review-detail-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  background: #F8FAFC;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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
  font-size: 22px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 2px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: #FFFFFF;
  border-radius: 20px;
}

.loading-state p,
.error-state p {
  margin-top: 16px;
  color: #64748B;
}

.loading-spinner {
  color: #0891B2;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.player-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.play-btn {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(8, 145, 178, 0.3);
}

.play-btn.playing {
  background: linear-gradient(135deg, #0E7490, #0891B2);
}

.play-btn svg {
  margin-left: 3px;
}

.progress-area {
  flex: 1;
}

.progress-bar {
  height: 6px;
  background: #E2E8F0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0891B2, #22D3EE);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.progress-time {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94A3B8;
}

.info-card {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #94A3B8;
}

.info-value {
  font-size: 14px;
  color: #1E293B;
  font-weight: 500;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  width: fit-content;
}

.status-badge.completed {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.status-badge.processing,
.status-badge.transcribed {
  background: rgba(8, 145, 178, 0.1);
  color: #0891B2;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #D97706;
}

.content-card,
.export-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.processing-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.processing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #64748B;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: #1E293B;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 8px;
  color: #0891B2;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(8, 145, 178, 0.15);
}

.transcript-text {
  font-size: 14px;
  line-height: 1.8;
  color: #475569;
  white-space: pre-wrap;
}

.summary-content {
  font-size: 14px;
  line-height: 1.8;
  color: #475569;
}

.summary-section {
  margin-bottom: 16px;
}

.summary-section:last-child {
  margin-bottom: 0;
}

.summary-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 4px;
}

.summary-section-text {
  color: #475569;
}

.memorable-quote {
  font-style: italic;
  color: #059669;
}

.export-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.export-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 12px;
  color: #475569;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-btn:hover {
  background: rgba(8, 145, 178, 0.12);
  border-color: rgba(8, 145, 178, 0.25);
  color: #0891B2;
}

.export-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.export-btn svg {
  color: #0891B2;
}
</style>