import adminApi from './index'
import logger from '@/utils/logger'

/**
 * 管理员认证相关API
 */
export const adminLogin = (username, password) => {
  logger.info('[AdminAPI] Login request:', { username })
  return adminApi.post('/admin/login', { username, password })
}

export const adminLogout = () => {
  logger.info('[AdminAPI] Logout request')
  return adminApi.post('/admin/logout')
}

export const getAdminProfile = () => {
  logger.debug('[AdminAPI] Get admin profile')
  return adminApi.get('/admin/profile')
}