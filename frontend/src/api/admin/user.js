import adminApi from './index'
import logger from '@/utils/logger'

/**
 * 用户管理相关API
 */
export const getUsers = (params) => {
  logger.debug('[AdminAPI] Fetch users:', params)
  return adminApi.get('/admin/users', { params })
}

export const getUserDetail = (id) => {
  logger.debug(`[AdminAPI] Fetch user detail: ${id}`)
  return adminApi.get(`/admin/users/${id}`)
}

export const updateUserStatus = (id, data) => {
  logger.info(`[AdminAPI] Update user ${id} status:`, data)
  return adminApi.post(`/admin/users/${id}/status`, data)
}

export const exportUsers = (params) => {
  logger.info('[AdminAPI] Export users:', params)
  return adminApi.get('/admin/users/export', {
    params,
    responseType: 'blob'
  })
}