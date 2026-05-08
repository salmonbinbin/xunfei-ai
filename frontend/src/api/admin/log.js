import adminApi from './index'
import logger from '@/utils/logger'

/**
 * 操作日志相关API
 */
export const getLogs = (params) => {
  logger.debug('[AdminAPI] Fetch logs:', params)
  return adminApi.get('/admin/logs', { params })
}

export const getLogActions = () => {
  logger.debug('[AdminAPI] Fetch log action types')
  return adminApi.get('/admin/logs/actions')
}