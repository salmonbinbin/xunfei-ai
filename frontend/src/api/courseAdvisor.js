import api from '@/utils/request'

/**
 * 获取学生画像
 * @returns {Promise<{
 *   major: string,
 *   grade: number,
 *   goal: string,
 *   gpa: number,
 *   completed_credits: number,
 *   required_credits: number,
 *   radar_data: {专业知识覆盖度: number, 目标匹配度: number, 能力偏向: number, 选课压力指数: number},
 *   ability_type: string,
 *   ai_suggestion: string
 * }>}
 */
export function getStudentProfile() {
  return api.get('/course-advisor/profile')
}

/**
 * 获取AI推荐课程
 * @param {Object} data - 推荐参数
 * @param {string} data.semester - 学期，如 "2024-1"
 * @param {string} data.category - 类别：all/mandatory/elective/cross_major
 * @param {string} [data.goal_filter] - 目标筛选：考研/考公/就业/出国
 * @param {number} [data.page] - 页码
 * @param {number} [data.page_size] - 每页数量
 * @returns {Promise<{courses: Array, total_credits: number, total: number, page: number, total_pages: number}>}
 */
export function getRecommendations(data) {
  return api.post('/course-advisor/recommend', data)
}

/**
 * 获取课程详情
 * @param {number} courseId - 课程ID
 * @returns {Promise<{
 *   course: Object,
 *   prerequisites: Array,
 *   alternatives: Array,
 *   popular_combinations: Array
 * }>}
 */
export function getCourseDetail(courseId) {
  return api.get(`/course-advisor/courses/${courseId}`)
}

/**
 * 对话咨询
 * @param {Object} data - 对话信息
 * @param {string} data.message - 用户消息
 * @param {Array<{role: string, content: string}>} [data.history] - 对话历史
 * @returns {Promise<{
 *   reply: string,
 *   recommended_courses: Array,
 *   suggestions: Array
 * }>}
 */
export function chatConsultation(data) {
  return api.post('/course-advisor/chat', data)
}

/**
 * 确认选课方案
 * @param {Object} data - 选课信息
 * @param {string} data.semester - 学期
 * @param {number[]} data.selected_courses - 选中的课程ID列表
 * @returns {Promise<{
 *   plan_id: number,
 *   message: string,
 *   conflicts: Array,
 *   total_credits: number
 * }>}
 */
export function confirmSelection(data) {
  return api.post('/course-advisor/confirm', data)
}

/**
 * 获取我的已选课程
 * @param {string} semester - 学期
 * @returns {Promise<{courses: Array}>}
 */
export function getMySelectedCourses(semester) {
  return api.get('/course-advisor/my-courses', { params: { semester } })
}

/**
 * 根据课程名称搜索课程
 * @param {string} name - 课程名称
 * @returns {Promise<{course: Object}>}
 */
export function searchCourseByName(name) {
  return api.get('/course-advisor/course/search', { params: { name } })
}