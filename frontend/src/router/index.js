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

  if (to.meta.requiresProfile === false && userStore.isLoggedIn) {
    next()
    return
  }

  if (to.meta.requiresAuth && userStore.isLoggedIn && !userStore.hasProfile) {
    next('/guide')
    return
  }

  if (to.meta.requiresAuth && userStore.isLoggedIn && userStore.hasProfile) {
    next()
    return
  }

  next()
})

export default router
