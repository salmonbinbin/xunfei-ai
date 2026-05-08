import axios from 'axios'
import logger from '@/utils/logger'

// 创建独立的 axios 实例用于管理端
const adminApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
adminApi.interceptors.request.use(
  (config) => {
    const adminToken = localStorage.getItem('admin_token')
    if (adminToken) {
      config.headers.Authorization = `Bearer ${adminToken}`
    }
    logger.debug(`[AdminAPI] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    logger.error('[AdminAPI] Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
adminApi.interceptors.response.use(
  (response) => {
    logger.debug(`[AdminAPI] Response ${response.status}: ${response.config.url}`)
    return response
  },
  (error) => {
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          logger.warn('[AdminAPI] Unauthorized, clearing admin token')
          localStorage.removeItem('admin_token')
          window.location.href = '/admin/login'
          break
        case 403:
          logger.warn('[AdminAPI] Forbidden:', response.data)
          break
        case 404:
          logger.warn('[AdminAPI] Not found:', response.config.url)
          break
        default:
          logger.error(`[AdminAPI] Error ${response.status}:`, response.data)
      }
    } else if (error.request) {
      logger.error('[AdminAPI] Network error - no response received')
    } else {
      logger.error('[AdminAPI] Request setup error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default adminApi