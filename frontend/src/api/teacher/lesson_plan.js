/**
 * 教师教案 API
 */
import api from '@/utils/request'

/**
 * 获取PPT模板主题列表
 * @param {Object} params - 查询参数
 * @param {string} params.style - 风格（简约/卡通/商务/创意/国风/清新/扁平/插画/节日）
 * @param {string} params.color - 颜色（蓝色/绿色/红色/紫色/黑色/灰色/黄色/粉色/橙色）
 * @param {string} params.industry - 行业（科技互联网/教育培训/政务/学院/电子商务/...）
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<{total: number, records: Array}>}
 */
export function getLessonPlanThemes(params) {
  return api.get('/teacher/lesson-plan/themes', { params })
}

/**
 * 创建教案（仅保存基本信息，不生成大纲/PPT）
 * @param {Object} data - 教案信息
 * @param {string} data.title - 教案标题（必填）
 * @param {string} data.course_name - 课程名称（可选）
 * @param {string} data.knowledge_points - 知识点描述（必填）
 * @param {string} data.target_audience - 授课对象（可选）
 * @param {number} data.teaching_hours - 课时数（可选）
 * @param {string} data.template_id - PPT模板ID（可选）
 * @returns {Promise<Object>}
 */
export function createLessonPlan(data) {
  return api.post('/teacher/lesson-plan/', data)
}

/**
 * 生成教学大纲（异步）
 * @param {Object} data - 生成参数
 * @param {number} data.plan_id - 教案ID
 * @param {string} data.knowledge_points - 更新的知识点（可选）
 * @returns {Promise<{sid: string, outline: Object}>}
 */
export function generateOutline(data) {
  return api.post('/teacher/lesson-plan/generate-outline', data)
}

/**
 * 生成PPT（异步，提交后返回sid，需轮询状态）
 * @param {Object} data - 生成参数
 * @param {number} data.plan_id - 教案ID
 * @param {Object} data.outline - 大纲数据（generateOutline返回的outline）
 * @param {string} data.template_id - 模板ID（可选）
 * @param {boolean} data.is_ai_image - 是否AI配图
 * @param {string} data.ai_image_type - AI配图类型（normal/advanced）
 * @param {boolean} data.is_card_note - 是否生成演讲备注
 * @returns {Promise<{sid: string, status: string}>}
 */
export function generatePpt(data) {
  return api.post('/teacher/lesson-plan/generate-ppt', data)
}

/**
 * 查询PPT生成状态
 * @param {string} sid - PPT任务ID
 * @returns {Promise<{ppt_status: string, ppt_url: string, total_pages: number, done_pages: number}>}
 */
export function getPptStatus(sid) {
  return api.get(`/teacher/lesson-plan/ppt-status/${sid}`)
}

/**
 * 获取教案详情
 * @param {number} planId - 教案ID
 * @returns {Promise<Object>}
 */
export function getLessonPlan(planId) {
  return api.get(`/teacher/lesson-plan/${planId}`)
}

/**
 * 获取教案列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<{items: Array, total: number, page: number, page_size: number}>}
 */
export function listLessonPlans(params) {
  return api.get('/teacher/lesson-plan/', { params })
}
