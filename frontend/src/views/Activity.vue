<template>
  <div class="activity-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
        </svg>
        校园活动助手
      </h1>
      <p class="page-subtitle">AI帮你策划活动方案，撰写宣传文案</p>
    </div>

    <!-- Tab 切换 -->
    <div class="tab-container">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 主内容区：左侧表单 + 右侧结果 -->
    <div class="main-content">
      <!-- 左侧：输入表单 -->
      <div class="form-card">
        <!-- 策划方案表单 -->
        <div v-show="activeTab === 'plan'" class="form-section">
          <div class="form-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
              <rect x="9" y="3" width="6" height="4" rx="2"/>
              <path d="M9 12h6"/>
              <path d="M9 16h6"/>
            </svg>
            活动策划信息
          </div>

          <div class="form-group">
            <label>活动类型</label>
            <div class="option-grid">
              <button
                v-for="type in activityTypes"
                :key="type"
                @click="planForm.activity_type = type"
                :class="['option-btn', { selected: planForm.activity_type === type }]"
              >
                {{ type }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>活动主题</label>
            <el-input
              v-model="planForm.theme"
              type="text"
              class="form-input"
              placeholder="请输入活动主题"
            />
          </div>

          <div class="form-group">
            <label>预计人数</label>
            <div class="option-grid">
              <button
                v-for="scale in scales"
                :key="scale"
                @click="planForm.scale = scale"
                :class="['option-btn', { selected: planForm.scale === scale }]"
              >
                {{ scale }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>预算范围</label>
            <div class="option-grid">
              <button
                v-for="budget in budgets"
                :key="budget"
                @click="planForm.budget = budget"
                :class="['option-btn', { selected: planForm.budget === budget }]"
              >
                {{ budget }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>活动时间</label>
            <el-date-picker
              v-model="planForm.activity_date"
              type="date"
              class="form-input"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </div>

          <div class="form-group">
            <label>特殊需求</label>
            <div class="checkbox-grid">
              <label
                v-for="req in requirements"
                :key="req"
                class="checkbox-item"
              >
                <input
                  type="checkbox"
                  :value="req"
                  v-model="planForm.requirements"
                />
                <span>{{ req }}</span>
              </label>
            </div>
          </div>

          <button
            class="submit-btn"
            @click="generatePlan"
            :disabled="loading || !planForm.activity_type || !planForm.theme || !planForm.scale || !planForm.budget"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            {{ loading ? '生成中...' : '生成策划方案' }}
          </button>
        </div>

        <!-- 宣传文案表单 -->
        <div v-show="activeTab === 'copy'" class="form-section">
          <div class="form-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            文案创作信息
          </div>

          <div class="form-group">
            <label>文案类型</label>
            <div class="option-grid">
              <button
                v-for="type in copyTypes"
                :key="type"
                @click="copyForm.copy_type = type"
                :class="['option-btn', { selected: copyForm.copy_type === type }]"
              >
                {{ type }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>文案风格</label>
            <div class="option-grid">
              <button
                v-for="style in copyStyles"
                :key="style"
                @click="copyForm.style = style"
                :class="['option-btn', { selected: copyForm.style === style }]"
              >
                {{ style }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>活动主题</label>
            <el-input
              v-model="copyForm.theme"
              type="text"
              class="form-input"
              placeholder="请输入活动主题"
            />
          </div>

          <div class="form-group">
            <label>活动时间</label>
            <el-date-picker
              v-model="copyForm.activity_date"
              type="date"
              class="form-input"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </div>

          <div class="form-group">
            <label>活动地点</label>
            <el-input
              v-model="copyForm.location"
              type="text"
              class="form-input"
              placeholder="请输入活动地点"
            />
          </div>

          <div class="form-group">
            <label>预计人数</label>
            <el-input-number
              v-model="copyForm.expected_count"
              :min="1"
              :max="10000"
              class="form-input-number"
            />
          </div>

          <button
            class="submit-btn"
            @click="generateCopy"
            :disabled="loading || !copyForm.copy_type || !copyForm.style || !copyForm.theme"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            {{ loading ? '生成中...' : '生成宣传文案' }}
          </button>
        </div>
      </div>

      <!-- 右侧：结果展示 -->
      <div class="result-card">
        <div class="result-header">
          <span class="result-title">{{ activeTab === 'plan' ? '策划方案' : '宣传文案' }}</span>
          <div class="result-actions" v-if="result">
            <button class="action-btn" @click="copyResult" title="复制">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
            </button>
            <button class="action-btn" @click="sendToFeishu" title="发送到飞书">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="result-content" v-if="result">
          <pre class="result-text">{{ result }}</pre>
        </div>

        <div class="result-placeholder" v-else>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
          <p>填写左侧信息，点击生成按钮</p>
          <p class="placeholder-hint">AI将为你生成专业的活动策划方案或宣传文案</p>
        </div>
      </div>
    </div>

    <!-- 飞书群选择弹窗 -->
    <el-dialog v-model="showFeishuDialog" title="发送到飞书群" width="400px" class="feishu-dialog">
      <div class="feishu-form">
        <div class="form-group">
          <label>选择群组</label>
          <el-select v-model="selectedGroup" placeholder="请选择群组" class="group-select">
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </div>
      </div>
      <template #footer>
        <button class="dialog-btn cancel" @click="showFeishuDialog = false">取消</button>
        <button class="dialog-btn confirm" @click="confirmSendFeishu" :disabled="!selectedGroup || sendingFeishu">
          <span v-if="sendingFeishu" class="loading-spinner small"></span>
          {{ sendingFeishu ? '发送中...' : '确认发送' }}
        </button>
      </template>
    </el-dialog>

    <!-- 底部留白（移动端适配） -->
    <div class="bottom-padding"></div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { generatePlan as generatePlanApi, generateCopy as generateCopyApi, sendFeishu as sendFeishuApi, getGroups } from '@/api/activity'
import { ElMessage } from 'element-plus'

// Tab 配置
const tabs = [
  { key: 'plan', label: '策划方案' },
  { key: 'copy', label: '宣传文案' }
]

// 状态
const activeTab = ref('plan')
const loading = ref(false)
const result = ref('')
const showFeishuDialog = ref(false)
const selectedGroup = ref('')
const groups = ref([])
const sendingFeishu = ref(false)

// 策划表单
const activityTypes = ['文艺', '体育', '学术', '志愿', '团建', '其他']
const scales = ['小规模', '中规模', '大规模']
const budgets = ['低', '中', '高']
const requirements = ['需要抽奖', '需要嘉宾', '室外活动', '线上活动']

const planForm = reactive({
  activity_type: '',
  theme: '',
  scale: '',
  budget: '',
  activity_date: '',
  requirements: []
})

// 文案表单
const copyTypes = ['海报主标题', '朋友圈', '公众号推文', '邀请函', '广播稿']
const copyStyles = ['活泼青春', '正式严肃', '温情暖心', '燃系热血']

const copyForm = reactive({
  copy_type: '',
  style: '',
  theme: '',
  activity_date: '',
  location: '',
  expected_count: null
})

// 加载群组列表
async function loadGroups() {
  try {
    const { data } = await getGroups()
    groups.value = data.groups || []
  } catch (error) {
    console.error('加载群组失败:', error)
  }
}

// 生成策划方案
async function generatePlan() {
  if (!planForm.activity_type || !planForm.theme || !planForm.scale || !planForm.budget) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  result.value = ''

  try {
    const apiData = {
      activity_type: planForm.activity_type,
      theme: planForm.theme,
      scale: planForm.scale,
      budget: planForm.budget,
      activity_time: planForm.activity_date || undefined,
      special_needs: planForm.requirements.length > 0 ? planForm.requirements : undefined
    }
    const { data } = await generatePlanApi(apiData)
    result.value = data.plan || data.result || data
  } catch (error) {
    console.error('生成策划方案失败:', error)
    ElMessage.error('生成策划方案失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 生成宣传文案
async function generateCopy() {
  if (!copyForm.copy_type || !copyForm.style || !copyForm.theme) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  result.value = ''

  try {
    const apiData = {
      copy_type: copyForm.copy_type,
      style: copyForm.style,
      activity_name: copyForm.theme,
      activity_content: `活动时间：${copyForm.activity_date || '待定'}，活动地点：${copyForm.location || '待定'}，预计人数：${copyForm.expected_count || '待定'}`
    }
    const { data } = await generateCopyApi(apiData)
    result.value = data.copy || data.result || data
  } catch (error) {
    console.error('生成宣传文案失败:', error)
    ElMessage.error('生成宣传文案失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 复制结果
function copyResult() {
  if (!result.value) return
  navigator.clipboard.writeText(result.value).then(() => {
    ElMessage.success('复制成功')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 发送到飞书
async function sendToFeishu() {
  if (!result.value) return
  await loadGroups()
  showFeishuDialog.value = true
}

async function confirmSendFeishu() {
  if (!selectedGroup.value) {
    ElMessage.warning('请选择群组')
    return
  }

  sendingFeishu.value = true
  try {
    await sendFeishuApi({
      group_id: selectedGroup.value,
      title: activeTab.value === 'plan' ? `【活动策划】${planForm.theme}` : `【宣传文案】${copyForm.theme}`,
      content: result.value
    })
    ElMessage.success('发送成功')
    showFeishuDialog.value = false
    selectedGroup.value = ''
  } catch (error) {
    console.error('发送失败:', error)
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    sendingFeishu.value = false
  }
}
</script>

<style scoped>
.activity-page {
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

/* Tab 切换 */
.tab-container {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 10px 24px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  color: #64748B;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  border-color: #0891B2;
  color: #0891B2;
}

.tab-btn.active {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border-color: transparent;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* 表单卡片 */
.form-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}

.form-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.form-title svg {
  color: #0891B2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
}

.form-input {
  width: 100%;
}

.form-input :deep(.el-input__wrapper) {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  box-shadow: none;
  padding: 12px 16px;
}

.form-input :deep(.el-input__inner) {
  color: #1E293B;
}

.form-input :deep(.el-input__inner::placeholder) {
  color: #CBD5E1;
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: #0891B2;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #0891B2;
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
}

.form-input-number {
  width: 100%;
}

.form-input-number :deep(.el-input-number__decrease),
.form-input-number :deep(.el-input-number__increase) {
  background: #F8FAFC;
  border-color: #E2E8F0;
}

.form-input-number :deep(.el-input-number__decrease:hover),
.form-input-number :deep(.el-input-number__increase:hover) {
  color: #0891B2;
}

/* 选项按钮组 */
.option-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-btn {
  padding: 8px 16px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  color: #64748B;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-btn:hover {
  border-color: #0891B2;
  color: #0891B2;
}

.option-btn.selected {
  background: rgba(8, 145, 178, 0.08);
  border-color: rgba(8, 145, 178, 0.3);
  color: #0891B2;
}

/* 多选框组 */
.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.checkbox-item:hover {
  border-color: #0891B2;
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #0891B2;
}

.checkbox-item span {
  font-size: 13px;
  color: #475569;
}

/* 提交按钮 */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 145, 178, 0.35);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
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

/* 结果卡片 */
.result-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  transition: all 0.3s ease;
}

.result-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 8px;
  color: #0891B2;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(8, 145, 178, 0.15);
  border-color: rgba(8, 145, 178, 0.25);
}

.result-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.result-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.8;
  color: #1E293B;
  font-family: inherit;
  margin: 0;
}

.result-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #CBD5E1;
}

.result-placeholder svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.result-placeholder p {
  font-size: 15px;
  margin-bottom: 4px;
  color: #94A3B8;
}

.placeholder-hint {
  font-size: 13px;
  color: #CBD5E1;
}

/* 飞书弹窗 */
.feishu-dialog :deep(.el-dialog) {
  border-radius: 16px;
}

.feishu-dialog :deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
}

.feishu-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
}

.feishu-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.feishu-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #E2E8F0;
}

.feishu-form .form-group {
  margin-bottom: 0;
}

.group-select {
  width: 100%;
}

.group-select :deep(.el-input__wrapper) {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  box-shadow: none;
}

.group-select :deep(.el-input__wrapper:hover) {
  border-color: #0891B2;
}

.dialog-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dialog-btn.cancel {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  color: #64748B;
  margin-right: 12px;
}

.dialog-btn.cancel:hover {
  border-color: #CBD5E1;
  color: #475569;
}

.dialog-btn.confirm {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  color: #FFFFFF;
}

.dialog-btn.confirm:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.dialog-btn.confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 底部留白 */
.bottom-padding {
  height: 40px;
}

/* 响应式 */
@media (max-width: 768px) {
  .activity-page {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .form-card,
  .result-card {
    padding: 16px;
  }

  .checkbox-grid {
    grid-template-columns: 1fr;
  }
}
</style>
