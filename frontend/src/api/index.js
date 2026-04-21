import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000  // 120秒，适配图片理解等耗时操作
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error

    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.warning('登录已过期，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.warning('没有权限执行此操作')
          break
        case 404:
          ElMessage.warning('请求的资源不存在')
          break
        case 422:
          const validationMsg = response.data?.error?.details
          ElMessage.warning(validationMsg || '数据验证失败')
          break
        case 502:
          ElMessage.error('第三方服务暂时不可用')
          break
        default:
          ElMessage.error(response.data?.error?.message || '操作失败，请稍后重试')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default api
