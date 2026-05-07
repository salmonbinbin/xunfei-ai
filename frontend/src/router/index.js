import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/teacher/login',
    name: 'TeacherLogin',
    component: () => import('@/views/teacher/TeacherLogin.vue'),
    meta: { guest: true }
  },
  {
    path: '/teacher/register',
    name: 'TeacherRegister',
    component: () => import('@/views/teacher/TeacherRegister.vue'),
    meta: { guest: true }
  },
  {
    path: '/teacher',
    component: () => import('@/layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '', name: 'TeacherHome', component: () => import('@/views/teacher/TeacherHome.vue') },
      { path: 'grade', name: 'TeacherGrade', component: () => import('@/views/teacher/TeacherGrade.vue') },
      { path: 'grade/:id', name: 'TeacherGradeDetail', component: () => import('@/views/teacher/TeacherGradeDetail.vue') },
      { path: 'notification', name: 'TeacherNotification', component: () => import('@/views/teacher/TeacherNotification.vue') },
      { path: 'lesson-plan', name: 'TeacherLessonPlan', component: () => import('@/views/teacher/TeacherLessonPlan.vue') },
      { path: 'profile', name: 'TeacherProfile', component: () => import('@/views/teacher/TeacherProfile.vue') },
    ]
  },
  {
    path: '/guide',
    name: 'Guide',
    component: () => import('@/views/Guide.vue'),
    meta: { requiresAuth: true, requiresProfile: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'timetable', name: 'Timetable', component: () => import('@/views/Timetable.vue') },
      { path: 'timetable/import', name: 'TimetableImport', component: () => import('@/views/TimetableImport.vue') },
      { path: 'schedule', name: 'Schedule', component: () => import('@/views/Schedule.vue') },
      { path: 'review', name: 'Review', component: () => import('@/views/Review.vue') },
      { path: 'review/:id', name: 'ReviewDetail', component: () => import('@/views/ReviewDetail.vue') },
      { path: 'translate', name: 'Translate', component: () => import('@/views/Translate.vue') },
      { path: 'course-advisor', name: 'CourseAdvisor', component: () => import('@/views/CourseAdvisor.vue') },
      { path: 'activity', name: 'Activity', component: () => import('@/views/Activity.vue') },
      { path: 'ai-sister', name: 'AISister', component: () => import('@/views/AISister.vue') },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 如果有 token 但没有 userInfo，先获取用户信息（页面刷新后 userInfo 为 null）
  if (userStore.token && !userStore.userInfo) {
    await userStore.fetchUser()
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
    return
  }

  // 根路径 / 如果已登录则正常显示，不重定向到 /guide
  if (to.path === '/' && userStore.isLoggedIn) {
    next()
    return
  }

  // 学生用户需要完善资料才能进入完整功能
  if (to.meta.requiresProfile === false && userStore.isLoggedIn) {
    next()
    return
  }

  // 只有学生用户且缺少资料时才重定向到 /guide
  // 教师用户有自己的专属路由 /teacher，不需要引导页
  if (to.meta.requiresAuth && userStore.isLoggedIn && !userStore.hasProfile) {
    // 从 JWT token 中解码 role
    const isTeacher = (() => {
      try {
        const token = userStore.token
        if (!token) return false
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.role === 'teacher'
      } catch {
        return false
      }
    })()
    if (!isTeacher) {
      next('/guide')
      return
    }
  }

  if (to.meta.requiresAuth && userStore.isLoggedIn && userStore.hasProfile) {
    next()
    return
  }

  next()
})

export default router
