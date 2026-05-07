<template>
  <div class="register-page">
    <div class="bg-decoration">
      <div class="shape-circle circle-1"></div>
      <div class="shape-circle circle-2"></div>
      <div class="shape-circle circle-3"></div>
    </div>

    <div class="register-container">
      <div class="form-panel">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">教师注册</h2>
            <p class="form-desc">创建教师账户，开启智能教学之旅</p>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="register-form"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="form.phone"
                placeholder="请输入手机号"
                size="large"
                :prefix-icon="PhoneIcon"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                size="large"
                :prefix-icon="LockIcon"
                show-password
              />
            </el-form-item>

            <el-form-item prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入姓名"
                size="large"
                :prefix-icon="UserIcon"
              />
            </el-form-item>

            <el-form-item prop="department">
              <el-input
                v-model="form.department"
                placeholder="请输入院系"
                size="large"
                :prefix-icon="OfficeIcon"
              />
            </el-form-item>

            <el-form-item prop="course">
              <el-input
                v-model="form.course"
                placeholder="请输入教授课程"
                size="large"
                :prefix-icon="BookIcon"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="submit-btn"
                native-type="submit"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <span class="footer-text">已有账户？</span>
            <router-link to="/teacher/login" class="link-btn">去登录</router-link>
          </div>
        </div>
      </div>

      <div class="brand-panel">
        <div class="brand-content">
          <div class="logo-badge">
            <svg class="logo-icon" width="56" height="56" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#logoGrad2)"/>
              <circle cx="24" cy="18" r="7" fill="white" fill-opacity="0.95"/>
              <circle cx="21.5" cy="17" r="1.5" fill="#0891B2"/>
              <circle cx="26.5" cy="17" r="1.5" fill="#0891B2"/>
              <path d="M21 21C21 21 22.5 23 24 23C25.5 23 27 21 27 21" stroke="#0891B2" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M14 34C14 29.5817 17.5817 26 22 26H26C30.4183 26 34 29.5817 34 34V36H14V34Z" fill="white" fill-opacity="0.95"/>
              <defs>
                <linearGradient id="logoGrad2" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#0891B2"/>
                  <stop offset="1" stop-color="#22D3EE"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-name">AI小商教师端</h1>
          <p class="brand-tagline">智能教学好帮手</p>

          <div class="features-list">
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <span>智能成绩管理</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <span>AI通知生成</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <span>智能备课教案</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { teacherRegister } from '@/api/teacherAuth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  phone: '',
  password: '',
  name: '',
  department: '',
  course: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请输入院系', trigger: 'blur' }
  ],
  course: [
    { required: true, message: '请输入教授课程', trigger: 'blur' }
  ]
}

const PhoneIcon = {
  render() {
    return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z' })
    ])
  }
}

const LockIcon = {
  render() {
    return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('rect', { x: 3, y: 11, width: 18, height: 11, rx: 2, ry: 2 }),
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M7 11V7a5 5 0 0110 0v4' })
    ])
  }
}

const UserIcon = {
  render() {
    return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2' }),
      h('circle', { cx: 12, cy: 7, r: 4 })
    ])
  }
}

const OfficeIcon = {
  render() {
    return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' })
    ])
  }
}

const BookIcon = {
  render() {
    return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' })
    ])
  }
}

async function handleRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await teacherRegister(form)
      userStore.token = res.data.data.access_token
      userStore.userInfo = res.data.data.teacher
      localStorage.setItem('token', res.data.data.access_token)
      ElMessage.success('注册成功')
      router.push('/teacher')
    } catch (error) {
      ElMessage.error(error.response?.data?.error?.message || '注册失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.5;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08), rgba(34, 211, 238, 0.04));
  top: -150px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.06), rgba(34, 211, 238, 0.02));
  bottom: -100px;
  right: -50px;
}

.circle-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.05), rgba(34, 211, 238, 0.02));
  top: 50%;
  right: 20%;
}

.register-container {
  display: flex;
  width: 900px;
  max-width: 100%;
  background: #FFFFFF;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(8, 145, 178, 0.1);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.form-panel {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  align-items: center;
}

.form-card {
  width: 100%;
  max-width: 340px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 32px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px;
}

.form-desc {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.register-form {
  margin-bottom: 24px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(8, 145, 178, 0.4);
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: #64748B;
}

.footer-text {
  color: #94A3B8;
}

.link-btn {
  color: #0891B2;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.link-btn:hover {
  text-decoration: underline;
}

.brand-panel {
  flex: 1;
  background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%);
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
  margin-bottom: 24px;
}

.logo-icon {
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.brand-tagline {
  font-size: 14px;
  opacity: 0.9;
  margin: 0 0 32px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  opacity: 0.9;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 0 0 1px #E2E8F0;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #CBD5E1;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.2);
}

@media (max-width: 768px) {
  .register-container {
    flex-direction: column-reverse;
    width: 100%;
  }

  .brand-panel {
    padding: 32px 24px;
  }

  .form-panel {
    padding: 32px 24px;
  }
}
</style>
