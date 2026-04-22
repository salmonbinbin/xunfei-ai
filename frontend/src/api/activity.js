import api from '@/utils/request'

/**
 * 生成活动策划方案
 * @param {Object} data - 活动信息
 * @param {string} data.activity_type - 活动类型：文艺/体育/学术/志愿/团建/其他
 * @param {string} data.theme - 活动主题
 * @param {string} data.scale - 规模：小规模/中规模/大规模
 * @param {string} data.budget - 预算：低/中/高
 * @param {string} data.activity_date - 活动时间
 * @param {string[]} data.requirements - 特殊需求
 * @returns {Promise<{plan: string}>}
 */
export function generatePlan(data) {
  return api.post('/activity/generate-plan', data)
}

/**
 * 生成宣传文案
 * @param {Object} data - 文案信息
 * @param {string} data.copy_type - 文案类型：海报主标题/朋友圈/公众号推文/邀请函/广播稿
 * @param {string} data.style - 文案风格：活泼青春/正式严肃/温情暖心/燃系热血
 * @param {string} data.theme - 活动主题
 * @param {string} data.activity_date - 活动时间
 * @param {string} data.location - 活动地点
 * @param {number} data.expected_count - 预计人数
 * @returns {Promise<{copy: string}>}
 */
export function generateCopy(data) {
  return api.post('/activity/generate-copy', data)
}

/**
 * 发送文案到飞书
 * @param {Object} data - 发送信息
 * @param {string} data.group_id - 群组ID
 * @param {string} data.content - 文案内容
 * @param {string} data.title - 标题
 * @returns {Promise<{message: string}>}
 */
export function sendFeishu(data) {
  return api.post('/activity/send-feishu', data)
}

/**
 * 获取可用群组列表
 * @returns {Promise<{groups: Array<{id: string, name: string}>}>}
 */
export function getGroups() {
  return api.get('/activity/groups')
}