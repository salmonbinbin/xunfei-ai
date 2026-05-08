import adminApi from './index'
import logger from '@/utils/logger'

/**
 * 数据看板相关API
 */
export const getDashboardStats = () => {
  logger.debug('[AdminAPI] Fetch dashboard stats')
  return adminApi.get('/admin/dashboard/stats')
}

export const getDashboardTrend = (date) => {
  logger.debug(`[AdminAPI] Fetch dashboard trend for date: ${date}`)
  return adminApi.get('/admin/dashboard/trend', { params: { date } })
}