<template>
  <div class="guide-page">
    <!-- 清新背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
    </div>

    <div class="guide-container">
      <div class="guide-card">
        <!-- Header -->
        <div class="card-header">
          <div class="logo-area">
            <svg class="logo-icon" width="56" height="56" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#guideLogoGrad)"/>
              <circle cx="24" cy="18" r="7" fill="white" fill-opacity="0.95"/>
              <circle cx="21.5" cy="17" r="1.5" fill="#6366F1"/>
              <circle cx="26.5" cy="17" r="1.5" fill="#6366F1"/>
              <path d="M21 21C21 21 22.5 23 24 23C25.5 23 27 21 27 21" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M14 34C14 29.5817 17.5817 26 24 26H28C33.5817 26 38 29.5817 38 34V36H14V34Z" fill="white" fill-opacity="0.95"/>
              <defs>
                <linearGradient id="guideLogoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#6366F1"/>
                  <stop offset="1" stop-color="#8B5CF6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="guide-title">欢迎加入AI小商</h1>
          <p class="guide-subtitle">完善资料，开启智慧校园之旅</p>

          <!-- 切换账号按钮 -->
          <button class="switch-account-btn" @click="handleSwitchAccount">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            切换账号
          </button>
        </div>

        <!-- 步骤指示器 -->
        <div class="steps-indicator">
          <div class="step active">
            <div class="step-badge">1</div>
            <span class="step-text">基本信息</span>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-badge pending">2</div>
            <span class="step-text">完成</span>
          </div>
        </div>

        <!-- 表单 -->
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="profile-form"
        >
          <el-form-item label="专业" prop="major">
            <el-input
              v-model="form.major"
              placeholder="请输入你的专业"
              size="large"
            />
          </el-form-item>

          <el-form-item label="年级" prop="grade">
            <el-select
              v-model="form.grade"
              placeholder="请选择年级"
              size="large"
              class="full-width"
            >
              <el-option :value="1" label="大一" />
              <el-option :value="2" label="大二" />
              <el-option :value="3" label="大三" />
              <el-option :value="4" label="大四" />
            </el-select>
          </el-form-item>

          <el-form-item label="班级" prop="class_name">
            <el-input
              v-model="form.class_name"
              placeholder="请输入班级名称"
              size="large"
            />
          </el-form-item>

          <el-form-item label="你的目标" prop="goal">
            <div class="goal-chips">
              <button
                v-for="option in goalOptions"
                :key="option.value"
                type="button"
                class="goal-chip"
                :class="{ active: form.goal === option.value }"
                @click="form.goal = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </el-form-item>

          <button
            type="button"
            class="submit-btn"
            :disabled="loading"
            @click="handleSubmit"
          >
            <span v-if="loading" class="spinner"></span>
            <span v-else>完成注册</span>
          </button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { updateProfile } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  major: '',
  grade: '',
  class_name: '',
  goal: ''
})

const goalOptions = [
  { value: '考研', label: '考研' },
  { value: '考公', label: '考公' },
  { value: '就业', label: '就业' },
  { value: '出国', label: '出国' },
  { value: '未定', label: '未定' }
]

const rules = {
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
  class_name: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  goal: [{ required: true, message: '请选择目标', trigger: 'change' }]
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await updateProfile(form)
    await userStore.fetchUser()
    ElMessage.success('资料完善成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function handleSwitchAccount() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.guide-page {
  --primary: #6366F1;
  --primary-light: #818CF8;
  --bg-page: #FAFBFC;
  --bg-card: #FFFFFF;
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --border: #E5E7EB;

  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;
}

.shape-1 {
  width: 450px;
  height: 450px;
  background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
  top: -180px;
  right: -120px;
}

.shape-2 {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, #F3E8FF, #E9D5FF);
  bottom: -120px;
  left: -80px;
}

/* 容器 */
.guide-container {
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 10;
}

.guide-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 36px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* 头部 */
.card-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo-area {
  margin-bottom: 16px;
}

.logo-icon {
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.25));
}

.guide-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.guide-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* 切换账号按钮 */
.switch-account-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-page);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.switch-account-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary);
  background: rgba(99, 102, 241, 0.05);
}

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-badge {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.step-badge.pending {
  background: var(--border);
  color: var(--text-muted);
}

.step-text {
  font-size: 12px;
  color: var(--primary);
  font-weight: 500;
}

.step:not(.active) .step-text {
  color: var(--text-muted);
}

.step-line {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, var(--primary), var(--border));
  margin: 0 12px;
  margin-bottom: 18px;
  border-radius: 1px;
}

/* 表单 */
.profile-form {
  margin-top: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 13px;
  padding-bottom: 6px !important;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background: var(--bg-page) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  padding: 2px 12px;
  min-height: 44px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover) {
  border-color: var(--primary-light) !important;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focused) {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

:deep(.el-input__inner),
:deep(.el-select__placeholder) {
  color: var(--text-primary) !important;
  font-size: 14px;
}

:deep(.el-input__inner::placeholder) {
  color: var(--text-muted) !important;
}

:deep(.el-select__caret) {
  color: var(--text-muted);
}

.full-width {
  width: 100%;
}

/* 目标选项 */
.goal-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.goal-chip {
  padding: 8px 16px;
  background: var(--bg-page);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.goal-chip:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

.goal-chip.active {
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border-color: var(--primary);
  color: white;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 14px 20px;
  margin-top: 12px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 480px) {
  .guide-card {
    padding: 28px 24px;
  }

  .guide-title {
    font-size: 22px;
  }

  .goal-chip {
    padding: 6px 12px;
    font-size: 12px;
  }

  .step-line {
    width: 50px;
  }
}
</style>
