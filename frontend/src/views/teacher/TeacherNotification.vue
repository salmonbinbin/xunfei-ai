<template>
  <div class="notification-page">
    <div class="page-header">
      <h1>智能通知发布</h1>
      <el-tag type="info" effect="plain">AI辅助生成</el-tag>
    </div>

    <div class="notification-layout">
      <!-- 左侧：输入表单 -->
      <div class="notification-form">
        <el-card class="form-card">
          <template #header>
            <span>通知信息</span>
          </template>

          <!-- 通知类型选择 -->
          <div class="type-section">
            <label class="form-label">通知类型</label>
            <div class="type-grid">
              <div
                v-for="type in notificationTypes"
                :key="type.value"
                :class="['type-item', { active: form.type === type.value }]"
                @click="form.type = type.value"
              >
                <span class="type-icon">{{ type.icon }}</span>
                <span class="type-name">{{ type.label }}</span>
              </div>
            </div>
          </div>

          <!-- 通知主题 -->
          <el-form-item label="通知主题" required class="form-item">
            <el-input
              v-model="form.topic"
              placeholder="例如：关于期末考试安排的通知"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <!-- 补充信息 -->
          <el-form-item label="补充信息" class="form-item">
            <el-input
              v-model="form.additionalInfo"
              type="textarea"
              :rows="3"
              placeholder="如考试时间、地点、会议议程等（选填）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <!-- 生成按钮 -->
          <el-button
            type="primary"
            :loading="generating"
            :disabled="!canGenerate"
            class="generate-btn"
            @click="handleGenerate"
          >
            {{ generating ? 'AI生成中...' : 'AI生成通知' }}
          </el-button>
        </el-card>
      </div>

      <!-- 右侧：生成结果 -->
      <div class="notification-result">
        <el-card class="result-card">
          <template #header>
            <span>生成结果</span>
          </template>

          <!-- 空状态 -->
          <div v-if="!result && !generating" class="result-placeholder">
            <div class="placeholder-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <p>请先填写通知信息并点击"AI生成通知"</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="generating" class="result-loading">
            <el-icon class="is-loading" :size="32">
              <Loading />
            </el-icon>
            <p>AI正在生成通知，请稍候...</p>
          </div>

          <!-- 生成结果 -->
          <div v-if="(result || generating) && !generating" class="result-content">
            <el-input
              v-model="result"
              type="textarea"
              :rows="12"
              placeholder="生成的通知内容将显示在这里，您可以手动修改"
              class="result-textarea"
            />
          </div>

          <template #footer>
            <div class="result-actions">
              <el-button
                :disabled="!result"
                @click="handleCopy"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                复制通知
              </el-button>
              <el-button
                type="primary"
                :disabled="!result"
                @click="showSendDialog = true"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px">
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
                发送到飞书群
              </el-button>
            </div>
          </template>
        </el-card>
      </div>
    </div>

    <!-- 飞书发送弹窗 -->
    <el-dialog
      v-model="showSendDialog"
      title="发送到飞书群"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="send-dialog-content">
        <p class="send-tip">选择要发送的飞书群组：</p>
        <el-select v-model="selectedGroup" placeholder="请选择群组" class="group-select">
          <el-option
            v-for="group in groups"
            :key="group.group_id"
            :label="group.name"
            :value="group.group_id"
          />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="showSendDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="sending"
          :disabled="!selectedGroup"
          @click="handleSendToFeishu"
        >
          确认发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { generateNotification, getGroups, sendToFeishu } from '@/api/teacherNotification'

// 通知类型配置
const notificationTypes = [
  { value: 'exam', label: '考试通知', icon: '📝', color: '#3B82F6' },
  { value: 'meeting', label: '会议通知', icon: '📅', color: '#8B5CF6' },
  { value: 'activity', label: '活动通知', icon: '🎉', color: '#10B981' },
  { value: 'holiday', label: '放假通知', icon: '🏖️', color: '#F59E0B' },
  { value: 'submission', label: '征稿通知', icon: '📢', color: '#EF4444' },
  { value: 'other', label: '其他通知', icon: '📋', color: '#6B7280' }
]

// 表单数据
const form = reactive({
  type: '',
  topic: '',
  additionalInfo: ''
})

// 状态
const generating = ref(false)
const sending = ref(false)
const result = ref('')
const resultTitle = ref('')
const showSendDialog = ref(false)
const selectedGroup = ref('')
const groups = ref([])

// 是否可以生成
const canGenerate = computed(() => {
  return form.type && form.topic.trim().length > 0 && !generating.value
})

// 加载群组列表
async function fetchGroups() {
  console.log('========== fetchGroups 开始 ==========')
  try {
    const res = await getGroups()
    console.log('getGroups响应:', JSON.stringify(res, null, 2))
    // GET请求返回的是数组，直接用res.data
    if (Array.isArray(res.data)) {
      groups.value = res.data || []
    } else if (res.data?.success) {
      groups.value = res.data.data || []
    }
    console.log('groups.value:', groups.value)
  } catch (error) {
    console.error('获取群组失败:', error)
  }
  console.log('========== fetchGroups 结束 ==========')
}

// 生成通知
async function handleGenerate() {
  console.log('========== handleGenerate 开始 ==========')
  console.log('form:', JSON.stringify(form))

  if (!canGenerate.value) {
    console.log('canGenerate 为 false，直接返回')
    return
  }

  generating.value = true
  result.value = ''

  try {
    console.log('开始调用 generateNotification API...')
    console.log('请求参数:', {
      notification_type: form.type,
      topic: form.topic,
      additional_info: form.additionalInfo || undefined
    })

    const res = await generateNotification({
      notification_type: form.type,
      topic: form.topic,
      additional_info: form.additionalInfo || undefined
    })

    console.log('API响应:', JSON.stringify(res, null, 2))
    console.log('res.data:', JSON.stringify(res.data, null, 2))

    if (res.data?.success) {
      console.log('生成成功，设置result')
      resultTitle.value = res.data.data.title
      result.value = res.data.data.content
      ElMessage.success('通知生成成功')
    } else {
      console.log('生成失败: res.data.success is false')
      console.log('错误信息:', res.data?.error?.message)
      ElMessage.error(res.data?.error?.message || '生成失败')
    }
  } catch (error) {
    console.error('========== 生成通知异常 ==========')
    console.error('error:', error)
    console.error('error.response:', error?.response)
    console.error('error.response?.data:', error?.response?.data)
    const errorMsg = error?.response?.data?.error?.message || error?.response?.data?.detail || error?.message || '生成失败，请重试'
    console.error('最终错误信息:', errorMsg)
    ElMessage.error(errorMsg)
  } finally {
    generating.value = false
    console.log('========== handleGenerate 结束 ==========')
  }
}

// 复制到剪贴板
async function handleCopy() {
  if (!result.value) return

  try {
    await navigator.clipboard.writeText(result.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = result.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('已复制到剪贴板')
  }
}

// 发送到飞书群
async function handleSendToFeishu() {
  if (!selectedGroup.value || !result.value) return

  sending.value = true

  try {
    const res = await sendToFeishu({
      title: resultTitle.value,
      content: result.value,
      group_id: selectedGroup.value
    })

    if (res.data?.success) {
      ElMessage.success('发送成功')
      showSendDialog.value = false
      selectedGroup.value = ''
    } else {
      ElMessage.error(res.data?.error?.message || '发送失败')
    }
  } catch (error) {
    console.error('发送失败:', error)
    const errorMsg = error?.response?.data?.detail || error?.message || '发送失败，请重试'
    ElMessage.error(errorMsg)
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  fetchGroups()
})
</script>

<style scoped>
.notification-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

/* 布局 */
.notification-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .notification-layout {
    grid-template-columns: 1fr;
  }
}

/* 表单卡片 */
.form-card {
  border-radius: 16px;
}

.type-section {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 12px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.type-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 8px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #FFFFFF;
}

.type-item:hover {
  border-color: #CBD5E1;
  background: #F8FAFC;
}

.type-item.active {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.04);
}

.type-icon {
  font-size: 24px;
}

.type-name {
  font-size: 12px;
  color: #475569;
}

.type-item.active .type-name {
  color: #0891B2;
  font-weight: 500;
}

.form-item {
  margin-bottom: 16px;
}

.generate-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
}

.generate-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

/* 结果卡片 */
.result-card {
  border-radius: 16px;
  height: fit-content;
}

.result-placeholder,
.result-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #94A3B8;
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(167, 139, 250, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8B5CF6;
  margin-bottom: 16px;
}

.result-placeholder p {
  font-size: 14px;
  margin: 0;
}

.result-loading p {
  margin-top: 16px;
  font-size: 14px;
}

.result-content {
  padding: 16px 0;
  min-height: 200px;
}

.result-textarea :deep(.el-textarea__inner) {
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  line-height: 1.8;
  color: #1E293B;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
}

.result-textarea :deep(.el-textarea__inner:focus) {
  border-color: #0891B2;
  box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.1);
}

.result-actions {
  display: flex;
  gap: 12px;
}

/* 发送弹窗 */
.send-dialog-content {
  padding: 16px 0;
}

.send-tip {
  font-size: 14px;
  color: #475569;
  margin: 0 0 12px;
}

.group-select {
  width: 100%;
}
</style>
