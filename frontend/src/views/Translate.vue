<template>
  <div class="translate-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
        智能翻译
      </h1>
      <p class="page-subtitle">即时文本翻译 · 文档翻译导出</p>
    </div>

    <!-- 即时翻译区域 -->
    <div class="translate-card">
      <div class="card-header">
        <h2>即时翻译</h2>
      </div>
      <div class="translate-content">
        <!-- 左侧输入区 -->
        <div class="translate-panel input-panel">
          <div class="panel-header">
            <span class="input-lang-badge">中文</span>
          </div>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="8"
            placeholder="请输入要翻译的中文文本..."
            resize="none"
            class="translate-input"
          />
          <div class="panel-footer">
            <span class="char-count">{{ inputText.length }}/5000</span>
            <button class="clear-btn" @click="clearInput" v-if="inputText">清空</button>
          </div>
        </div>

        <!-- 中间操作区 -->
        <div class="translate-action">
          <div class="action-content">
            <el-select v-model="targetLang" size="default" class="lang-select target-select">
              <el-option
                v-for="lang in targetLangOptions"
                :key="lang.code"
                :label="lang.name"
                :value="lang.code"
              />
            </el-select>
            <button
              class="translate-btn"
              @click="doTranslate"
              :disabled="!inputText.trim() || translateLoading"
            >
              <span v-if="translateLoading" class="loading-spinner"></span>
              <span v-else>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
                翻译
              </span>
            </button>
          </div>
        </div>

        <!-- 右侧输出区 -->
        <div class="translate-panel output-panel">
          <div class="panel-header">
            <span class="output-label">翻译结果</span>
            <button class="copy-btn" @click="copyResult" v-if="translatedText" title="复制结果">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              复制
            </button>
          </div>
          <div class="translate-output">
            <p v-if="!translatedText && !translateLoading" class="placeholder-text">
              翻译结果将显示在这里
            </p>
            <p v-else-if="translateLoading" class="loading-text">
              <span class="loading-spinner small"></span>
              翻译中...
            </p>
            <p v-else class="result-text">{{ translatedText }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档翻译区域 -->
    <div class="translate-card">
      <div class="card-header">
        <h2>文档翻译</h2>
        <span class="supported-types">支持 .txt, .docx 文件</span>
      </div>

      <!-- 文件上传 -->
      <div
        class="upload-area"
        :class="{ 'has-file': uploadFile, 'drag-over': isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.docx"
          @change="handleFileChange"
          style="display: none"
        />
        <div v-if="!uploadFile" class="upload-placeholder">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="12" y1="18" x2="12" y2="12"/>
            <line x1="9" y1="15" x2="15" y2="15"/>
          </svg>
          <p class="upload-text">点击或拖拽文件到此处上传</p>
          <p class="upload-hint">支持 txt, docx 格式</p>
        </div>
        <div v-else class="file-info">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <div class="file-details">
            <p class="file-name">{{ uploadFile.name }}</p>
            <p class="file-size">{{ formatFileSize(uploadFile.size) }}</p>
          </div>
          <button class="remove-file" @click.stop="removeFile">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 翻译选项 -->
      <div class="doc-options">
        <div class="option-item">
          <label>目标语言：</label>
          <el-select v-model="docTargetLang" size="default" class="doc-lang-select">
            <el-option
              v-for="lang in targetLangOptions"
              :key="lang.code"
              :label="lang.name"
              :value="lang.code"
            />
          </el-select>
        </div>
        <button
          class="doc-translate-btn"
          @click="translateDocument"
          :disabled="!uploadFile || docTranslateLoading"
        >
          <span v-if="docTranslateLoading" class="loading-spinner"></span>
          <span v-else>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            翻译文档
          </span>
        </button>
      </div>

      <!-- 翻译状态 -->
      <div v-if="docStatus" class="doc-status" :class="docStatus">
        <span v-if="docStatus === 'processing'" class="status-processing">
          <span class="loading-spinner small"></span>
          翻译中，请稍候...
        </span>
        <span v-else-if="docStatus === 'completed'" class="status-completed">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          翻译完成！词数：{{ docWordCount }}
        </span>
        <span v-else-if="docStatus === 'failed'" class="status-failed">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          翻译失败：{{ docErrorMessage }}
        </span>
      </div>

      <!-- 翻译预览 -->
      <div v-if="docTranslatedContent" class="doc-preview">
        <div class="preview-header">
          <h3>翻译预览</h3>
          <button class="download-btn" @click="downloadDoc">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            下载Word文档
          </button>
        </div>
        <div class="preview-content">
          <p class="preview-text">{{ docTranslatedContent }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { translateText, translateDocx, getTranslationPreview, downloadTranslation } from '@/api/translate'

// 语言选项
const languages = [
  { code: 'cn', name: '中文' },
  { code: 'en', name: '英文' },
  { code: 'ja', name: '日文' },
  { code: 'ko', name: '韩文' },
  { code: 'fr', name: '法文' },
  { code: 'de', name: '德文' },
  { code: 'es', name: '西班牙文' },
  { code: 'ru', name: '俄文' },
  { code: 'ar', name: '阿拉伯文' }
]

const sourceLangOptions = computed(() => languages)
// 即时翻译 - 源语言固定为中文，目标语言可选
const targetLangOptions = computed(() => languages.filter(l => l.code !== 'cn'))

const inputText = ref('')
const targetLang = ref('en')  // 默认目标语言英文
const translatedText = ref('')
const translateLoading = ref(false)

function clearInput() {
  inputText.value = ''
  translatedText.value = ''
}

async function doTranslate() {
  if (!inputText.value.trim()) return

  translateLoading.value = true
  translatedText.value = ''

  try {
    // 源语言固定为中文
    console.log('[Translate] Calling API with:', { text: inputText.value, target: targetLang.value })
    const response = await translateText(inputText.value, 'cn', targetLang.value)
    console.log('[Translate] API Response:', JSON.stringify(response))
    console.log('[Translate] Response data:', JSON.stringify(response?.data))

    // 正确提取翻译结果 - 后端返回格式是 {success: true, data: {translated_text: "Hello"}}
    // axios的response.data是后端的响应体，所以实际访问路径是 response.data.data.translated_text
    const resultData = response?.data?.data || response?.data
    if (resultData?.translated_text) {
      translatedText.value = resultData.translated_text
    } else {
      console.warn('[Translate] No translated_text in response:', resultData)
    }
    console.log('[Translate] Final translatedText:', translatedText.value)
  } catch (error) {
    console.error('[Translate] Text translation failed:', error)
    console.error('[Translate] Error response:', error?.response)
    ElMessage.error(error?.response?.data?.error?.message || '翻译失败，请稍后重试')
  } finally {
    translateLoading.value = false
  }
}

async function copyResult() {
  if (!translatedText.value) return
  try {
    await navigator.clipboard.writeText(translatedText.value)
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 文档翻译
const fileInput = ref(null)
const uploadFile = ref(null)
const isDragOver = ref(false)
const docTargetLang = ref('en')  // 目标语言默认英文
const docTranslateLoading = ref(false)
const docStatus = ref('')
const docWordCount = ref(0)
const docErrorMessage = ref('')
const docTranslatedContent = ref('')
const currentTaskId = ref('')

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (file) {
    setUploadFile(file)
  }
}

function handleDrop(event) {
  isDragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext === 'txt' || ext === 'docx') {
      setUploadFile(file)
    } else {
      ElMessage.error('仅支持 txt 和 docx 格式文件')
    }
  }
}

function setUploadFile(file) {
  uploadFile.value = file
  docStatus.value = ''
  docTranslatedContent.value = ''
  currentTaskId.value = ''
}

function removeFile() {
  uploadFile.value = null
  docStatus.value = ''
  docTranslatedContent.value = ''
  currentTaskId.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function translateDocument() {
  if (!uploadFile.value) return

  docTranslateLoading.value = true
  docStatus.value = 'processing'
  docErrorMessage.value = ''
  docTranslatedContent.value = ''
  currentTaskId.value = ''

  try {
    console.log('[Translate] Uploading file:', uploadFile.value.name, 'target:', docTargetLang.value)
    const response = await translateDocx(uploadFile.value, docTargetLang.value)
    console.log('[Translate] Upload response:', response)
    console.log('[Translate] Upload response.data:', JSON.stringify(response?.data))

    // 正确提取task_id - 后端返回格式是 {success: true, data: {task_id: "xxx", status: "completed"}}
    const resultData = response?.data?.data || response?.data
    currentTaskId.value = resultData?.task_id || ''
    console.log('[Translate] Task ID:', currentTaskId.value)

    if (!currentTaskId.value) {
      throw new Error('未获取到任务ID')
    }

    // 轮询获取翻译结果
    await pollTranslationResult(currentTaskId.value)
  } catch (error) {
    console.error('[Translate] Document translation failed:', error)
    docStatus.value = 'failed'
    docErrorMessage.value = error?.response?.data?.error?.message || error.message || '翻译失败，请稍后重试'
  } finally {
    docTranslateLoading.value = false
  }
}

async function pollTranslationResult(taskId) {
  const maxAttempts = 60
  let attempts = 0

  while (attempts < maxAttempts) {
    try {
      const response = await getTranslationPreview(taskId)
      console.log('[Translate] Poll response:', JSON.stringify(response?.data))

      // 正确提取数据 - 后端返回格式是 {success: true, data: {status: "completed", ...}}
      const resultData = response?.data?.data || response?.data
      const status = resultData?.status

      console.log('[Translate] Poll status:', status, 'attempts:', attempts)

      if (status === 'completed') {
        docStatus.value = 'completed'
        docWordCount.value = resultData?.word_count || 0
        docTranslatedContent.value = resultData?.translated_content || ''
        return
      } else if (status === 'failed') {
        docStatus.value = 'failed'
        docErrorMessage.value = resultData?.error_message || '翻译失败'
        return
      }

      attempts++
      await new Promise(resolve => setTimeout(resolve, 1000))
    } catch (error) {
      console.error('[Translate] Poll failed:', error)
      attempts++
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }

  docStatus.value = 'failed'
  docErrorMessage.value = '翻译超时，请稍后重试'
}

async function downloadDoc() {
  if (!currentTaskId.value) return

  try {
    const response = await downloadTranslation(currentTaskId.value)
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `translated_${currentTaskId.value}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('[Translate] Download failed:', error)
    ElMessage.error('下载失败，请稍后重试')
  }
}
</script>

<style scoped>
.translate-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  padding-bottom: 100px;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.page-title svg {
  color: #0891B2;
}

.page-subtitle {
  color: #94A3B8;
  font-size: 14px;
  margin: 0;
}

/* 翻译卡片 */
.translate-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.translate-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.supported-types {
  font-size: 12px;
  color: #94A3B8;
}

/* 即时翻译内容区 */
.translate-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: stretch;
}

@media (max-width: 768px) {
  .translate-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
}

.translate-panel {
  display: flex;
  flex-direction: column;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
  min-height: 280px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.lang-select {
  width: 140px;
}

.input-lang-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  border-radius: 6px;
  font-size: 13px;
  color: #0891B2;
  font-weight: 500;
}

.swap-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s ease;
}

.swap-btn:hover {
  background: #0891B2;
  border-color: #0891B2;
  color: #FFFFFF;
}

.translate-input :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 15px;
  line-height: 1.6;
  color: #1E293B;
  flex: 1;
}

.translate-input :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.panel-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #E2E8F0;
}

.char-count {
  font-size: 12px;
  color: #94A3B8;
}

.clear-btn {
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #F1F5F9;
  color: #64748B;
}

/* 中间操作区 */
.translate-action {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.target-select {
  width: 140px;
}

.translate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 120px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.translate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 145, 178, 0.35);
}

.translate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 右侧输出区 */
.output-panel {
  background: #FFFFFF;
}

.output-label {
  font-size: 14px;
  font-weight: 500;
  color: #64748B;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 6px;
  color: #0891B2;
  font-size: 12px;
  padding: 4px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(8, 145, 178, 0.15);
}

.translate-output {
  flex: 1;
  overflow-y: auto;
}

.placeholder-text {
  color: #CBD5E1;
  font-size: 14px;
  text-align: center;
  padding-top: 60px;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #0891B2;
  font-size: 14px;
  padding-top: 60px;
}

.result-text {
  font-size: 15px;
  line-height: 1.6;
  color: #1E293B;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Loading动画 */
.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner.small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(8, 145, 178, 0.2);
  border-top-color: #0891B2;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 文件上传 */
.upload-area {
  background: #F8FAFC;
  border: 2px dashed #E2E8F0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.02);
}

.upload-area.drag-over {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.05);
}

.upload-area.has-file {
  border-style: solid;
  border-color: #059669;
  background: rgba(5, 150, 105, 0.02);
}

.upload-placeholder svg {
  color: #CBD5E1;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: #64748B;
  margin: 0 0 4px 0;
}

.upload-hint {
  font-size: 12px;
  color: #94A3B8;
  margin: 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}

.file-info svg {
  color: #059669;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin: 0 0 4px 0;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: #94A3B8;
  margin: 0;
}

.remove-file {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  color: #94A3B8;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.remove-file:hover {
  background: #FEE2E2;
  color: #EF4444;
}

/* 文档翻译选项 */
.doc-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-item label {
  font-size: 14px;
  color: #64748B;
}

.doc-lang-select {
  width: 140px;
}

.doc-translate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 32px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.doc-translate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 145, 178, 0.35);
}

.doc-translate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 文档状态 */
.doc-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 16px;
  font-size: 14px;
}

.doc-status.processing {
  background: rgba(8, 145, 178, 0.08);
  color: #0891B2;
}

.doc-status.completed {
  background: rgba(5, 150, 105, 0.08);
  color: #059669;
}

.doc-status.failed {
  background: rgba(239, 68, 68, 0.08);
  color: #EF4444;
}

.status-processing,
.status-completed,
.status-failed {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 文档预览 */
.doc-preview {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #E2E8F0;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.preview-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #059669, #34D399);
  border: none;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.2);
}

.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.preview-content {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.preview-text {
  font-size: 14px;
  line-height: 1.8;
  color: #1E293B;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .translate-page {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .translate-card {
    padding: 16px;
  }

  .translate-panel {
    min-height: 200px;
  }

  .doc-options {
    flex-direction: column;
    align-items: stretch;
  }

  .doc-translate-btn {
    width: 100%;
  }
}
</style>
