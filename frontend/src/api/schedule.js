import api from '@/api'

/**
 * 获取日程列表
 * @param {Object} params - 查询参数
 * @param {number} [params.day_of_week] - 星期几
 * @param {number} [params.is_completed] - 是否完成
 * @returns {Promise<Array>}
 */
export function getSchedules(params) {
  return api.get('/schedule', { params })
}

/**
 * 创建日程（自然语言）
 * @param {string} text - 自然语言描述，如"周二上午9点去9教开会"
 * @returns {Promise<object>}
 */
export function createSchedule(text) {
  // 后端 ScheduleCreate 期望 event 字段
  return api.post('/schedule', { event: text })
}

/**
 * 删除日程
 * @param {number} id - 日程ID
 * @returns {Promise<object>}
 */
export function deleteSchedule(id) {
  return api.delete(`/schedule/${id}`)
}
