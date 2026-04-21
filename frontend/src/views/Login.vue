<template>
  <div class="login-page">
    <!-- 清新背景装饰 -->
    <div class="bg-decoration">
      <div class="shape-circle circle-1"></div>
      <div class="shape-circle circle-2"></div>
      <div class="shape-circle circle-3"></div>
      <div class="shape-dots"></div>
    </div>

    <div class="login-container">
      <!-- 左侧品牌区域 -->
      <div class="brand-panel">
        <div class="brand-content">
          <div class="logo-badge">
            <svg class="logo-icon" width="56" height="56" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#logoGrad)"/>
              <circle cx="24" cy="18" r="7" fill="white" fill-opacity="0.95"/>
              <circle cx="21.5" cy="17" r="1.5" fill="#6366F1"/>
              <circle cx="26.5" cy="17" r="1.5" fill="#6366F1"/>
              <path d="M21 21C21 21 22.5 23 24 23C25.5 23 27 21 27 21" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M14 34C14 29.5817 17.5817 26 22 26H26C30.4183 26 34 29.5817 34 34V36H14V34Z" fill="white" fill-opacity="0.95"/>
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#6366F1"/>
                  <stop offset="1" stop-color="#8B5CF6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-name">AI小商</h1>
          <p class="brand-tagline">你的智慧校园伙伴</p>

          <div class="features-preview">
            <div class="feature">
              <div class="feature-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                </svg>
              </div>
              <span>智能课表</span>
            </div>
            <div class="feature">
              <div class="feature-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <span>AI学姐</span>
            </div>
            <div class="feature">
              <div class="feature-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                </svg>
              </div>
              <span>录音回顾</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="form-panel">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">{{ mode === 'login' ? '欢迎回来' : '加入AI小商' }}</h2>
            <p class="form-desc">{{ mode === 'login' ? '登录您的账户继续探索' : '创建账户，开启智慧校园之旅' }}</p>
          </div>

          <!-- 登录/注册切换 -->
          <div class="auth-tabs">
            <button
              class="auth-tab"
              :class="{ active: mode === 'login' }"
              @click="mode = 'login'"
            >
              登录
            </button>
            <button
              class="auth-tab"
              :class="{ active: mode === 'register' }"
              @click="mode = 'register'"
            >
              注册
            </button>
          </div>

          <form class="auth-form" @submit.prevent="handleSubmit">
            <div class="field">
              <label class="field-label">手机号</label>
              <div class="input-wrap">
                <span class="input-prefix">+86</span>
                <input
                  v-model="formData.username"
                  type="tel"
                  class="field-input"
                  placeholder="请输入手机号"
                  maxlength="11"
                />
              </div>
              <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
            </div>

            <!-- 注册模式显示学号输入 -->
            <div v-if="mode === 'register'" class="field">
              <label class="field-label">学号</label>
              <div class="input-wrap">
                <input
                  v-model="formData.student_id"
                  type="text"
                  class="field-input"
                  placeholder="请输入学号"
                />
              </div>
              <span v-if="errors.student_id" class="field-error">{{ errors.student_id }}</span>
            </div>

            <div class="field">
              <label class="field-label">密码</label>
              <div class="input-wrap">
                <input
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="field-input"
                  :placeholder="mode === 'register' ? '设置密码（至少6位）' : '请输入密码'"
                />
                <button type="button" class="toggle-pwd" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
            </div>

            <!-- 注册模式额外显示昵称输入 -->
            <div v-if="mode === 'register'" class="field">
              <label class="field-label">昵称 <span class="optional">（选填）</span></label>
              <div class="input-wrap">
                <input
                  v-model="formData.nickname"
                  type="text"
                  class="field-input"
                  placeholder="给自己起个昵称"
                />
              </div>
            </div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>{{ mode === 'login' ? '登 录' : '立即注册' }}</span>
            </button>
          </form>

          <p class="terms">
            {{ mode === 'login' ? '登录即表示同意' : '注册即表示同意' }}
            <a href="#" class="terms-link">《用户协议》</a>和<a href="#" class="terms-link">《隐私政策》</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const mode = ref('login')
const showPassword = ref(false)

const formData = ref({
  username: '',
  student_id: '',
  password: '',
  nickname: ''
})

const errors = reactive({
  username: '',
  student_id: '',
  password: ''
})

function validateForm() {
  errors.username = ''
  errors.student_id = ''
  errors.password = ''

  const phoneRegex = /^1[3-9]\d{9}$/
  if (!formData.value.username) {
    errors.username = '请输入手机号'
    return false
  }
  if (!phoneRegex.test(formData.value.username)) {
    errors.username = '手机号格式不正确'
    return false
  }

  // 注册时需要学号
  if (mode.value === 'register' && !formData.value.student_id) {
    errors.student_id = '请输入学号'
    return false
  }

  if (!formData.value.password) {
    errors.password = '请输入密码'
    return false
  }
  if (mode.value === 'register' && formData.value.password.length < 6) {
    errors.password = '密码至少需要6位'
    return false
  }

  return true
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  try {
    if (mode.value === 'login') {
      await userStore.login(formData.value)
    } else {
      await userStore.register(formData.value)
    }

    if (userStore.hasProfile) {
      router.push('/')
    } else {
      router.push('/guide')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || (mode.value === 'login' ? '登录失败，请稍后重试' : '注册失败，请稍后重试'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 清新配色系统 */
.login-page {
  --primary: #6366F1;
  --primary-light: #818CF8;
  --primary-dark: #4F46E5;
  --accent: #10B981;
  --bg-page: #FAFBFC;
  --bg-card: #FFFFFF;
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --border: #E5E7EB;
  --border-light: #F3F4F6;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 25px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}

.login-page {
  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.shape-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
}

.circle-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  top: -200px;
  right: -150px;
}

.circle-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  bottom: -150px;
  left: -100px;
}

.circle-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  top: 40%;
  left: 10%;
}

.shape-dots {
  position: absolute;
  top: 20%;
  right: 5%;
  width: 100px;
  height: 100px;
  background-image: radial-gradient(#C7D2FE 1.5px, transparent 1.5px);
  background-size: 12px 12px;
  opacity: 0.5;
}

/* 登录容器 - 左右分栏 */
.login-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: var(--bg-card);
  border-radius: 28px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  position: relative;
  z-index: 10;
}

/* 左侧品牌面板 */
.brand-panel {
  flex: 1;
  background: linear-gradient(160deg, #6366F1 0%, #8B5CF6 100%);
  padding: 48px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-content {
  text-align: center;
  color: white;
}

.logo-badge {
  margin-bottom: 20px;
}

.logo-icon {
  filter: drop-shadow(0 8px 16px rgba(99, 102, 241, 0.35));
}

.brand-name {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: 3px;
  margin-bottom: 8px;
}

.brand-tagline {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 48px;
  letter-spacing: 1px;
}

.features-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.feature {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 15px;
  opacity: 0.95;
}

.feature-icon {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  opacity: 1;
}

/* 右侧表单面板 */
.form-panel {
  flex: 1;
  padding: 48px 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card {
  width: 100%;
  max-width: 320px;
}

.form-header {
  margin-bottom: 28px;
}

.form-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 认证切换标签 */
.auth-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 28px;
  background: var(--border-light);
  padding: 4px;
  border-radius: 12px;
}

.auth-tab {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.auth-tab:hover {
  color: var(--text-primary);
}

.auth-tab.active {
  background: var(--bg-card);
  color: var(--primary);
  box-shadow: var(--shadow-sm);
}

/* 表单 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.optional {
  font-weight: 400;
  color: var(--text-muted);
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix {
  position: absolute;
  left: 14px;
  font-size: 14px;
  color: var(--text-muted);
  pointer-events: none;
}

.field-input {
  width: 100%;
  padding: 12px 14px;
  padding-left: 44px;
  background: var(--bg-page);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.field-input::placeholder {
  color: var(--text-muted);
}

.field-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-card);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

/* 密码输入框特殊处理 */
.field:not(:first-child) .field-input {
  padding-left: 14px;
}

.toggle-pwd {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-pwd:hover {
  color: var(--text-secondary);
}

.field-error {
  font-size: 12px;
  color: #EF4444;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 13px 20px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
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

/* 协议 */
.terms {
  margin-top: 24px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.6;
}

.terms-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.terms-link:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    max-width: 420px;
  }

  .brand-panel {
    padding: 36px 28px;
  }

  .features-preview {
    display: none;
  }

  .form-panel {
    padding: 36px 28px;
  }
}
</style>
