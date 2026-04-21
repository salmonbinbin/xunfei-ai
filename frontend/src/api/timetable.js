import api from '@/api'

/**
 * 获取今日课程
 * @returns {Promise<{courses: Array, schedules: Array}>}
 */
export function getTodayCourses() {
  return api.get('/timetable/today')
}

/**
 * 获取课程列表
 * @param {number} [dayOfWeek] - 星期几 (1-7)
 * @returns {Promise<Array>}
 */
export function getCourses(dayOfWeek) {
  return api.get('/timetable', {
    params: dayOfWeek ? { day_of_week: dayOfWeek } : {}
  })
}

/**
 * 获取周课表
 * @param {number} weekOffset - 周偏移量（0=本周）
 * @returns {Promise<{week_start: string, courses: object}>}
 */
export function getWeekTimetable(weekOffset = 0) {
  return api.get('/timetable/week', { params: { week_offset: weekOffset } })
}

/**
 * 获取单节课详情（含AI洞察）
 * @param {number} courseId - 课程ID
 * @returns {Promise<object>}
 */
export function getCourseDetail(courseId) {
  return api.get(`/timetable/courses/${courseId}`)
}


/**
 * 导入课表（OCR识别 - 预览）
 * @param {File} imageFile - 课表图片文件
 * @returns {Promise<{message: string, courses: Array, raw_markdown: string}>}
 */
export function importTimetablePreview(imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)
  return api.post('/timetable/import/preview', formData)
}

/**
 * 上传课表图片（OCR识别 + AI解析）
 * @param {File} imageFile - 课表图片文件
 * @returns {Promise<{success: boolean, message: string, raw_text: string, courses: Array}>}
 */
export function uploadTimetable(imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)
  return api.post('/timetable/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 确认导入课表
 * @param {Array} courses - 课程列表
 * @param {string} semesterStartDate - 学期开始日期，如2025-03-03
 * @returns {Promise<{message: string, courses_count: number}>}
 */
export function importTimetableConfirm(courses, semesterStartDate) {
  return api.post('/timetable/import/confirm', {
    courses,
    semester_start_date: semesterStartDate
  })
}

/**
 * 清空所有课程
 * @returns {Promise<{success: boolean, message: string, deleted_count: number}>}
 */
export function clearAllCourses() {
  return api.delete('/timetable/courses/clear')
}

/**
 * 删除课程
 * @param {number} courseId - 课程ID
 * @returns {Promise<{success: boolean}>}
 */
export function deleteCourse(courseId) {
  return api.delete(`/timetable/course/${courseId}`)
}

/**
 * 更新课程信息
 * @param {number} courseId - 课程ID
 * @param {object} data - 更新数据
 * @returns {Promise<object>}
 */
export function updateCourse(courseId, data) {
  return api.put(`/timetable/course/${courseId}`, data)
}

/**
 * 生成AI学习建议
 * @param {number} courseId - 课程ID
 * @returns {Promise<{success: boolean, insight: object}>}
 */
export function generateAIInsights(courseId) {
  return api.post(`/timetable/ai-insights/${courseId}`)
}

/**
 * AI学伴问答
 * @param {number} courseId - 课程ID
 * @param {string} question - 问题
 * @returns {Promise<{answer: string, course_id: number}>}
 */
export function aiChatAboutCourse(courseId, question) {
  return api.post('/timetable/ai-chat', { course_id: courseId, question })
}
