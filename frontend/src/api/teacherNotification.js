/**
 * 教师通知 API
 */
import api from '@/utils/request'

/**
 * 生成通知
 * @param {Object} data - 通知信息
 * @param {string} data.notification_type - 通知类型: exam/meeting/activity/holiday/submission/other
 * @param {string} data.topic - 通知主题
 * @param {string} data.additional_info - 补充信息
 * @returns {Promise<{title: string, content: string}>}
 */
export function generateNotification(data) {
  return api.post('/teacher/notification/generate', data)
}

/**
 * 获取可用群组列表
 * @returns {Promise<Array<{group_id: string, name: string}>>}
 */
export function getGroups() {
  return api.get('/teacher/notification/groups')
}

/**
 * 发送通知到飞书群
 * @param {Object} data - 发送信息
 * @param {string} data.title - 通知标题
 * @param {string} data.content - 通知内容
 * @param {string} data.group_id - 群组ID
 * @returns {Promise<{message: string}>}
 */
export function sendToFeishu(data) {
  return api.post('/teacher/notification/send', data)
}
