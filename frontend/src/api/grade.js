import api from './index'

/**
 * 上传成绩Excel
 * @param {FormData} formData - 包含file, course_name, semester, class_name, weights_json
 */
export function uploadGrade(formData) {
  return api.post('/teacher/grade/upload', formData)
}

/**
 * 获取成绩记录列表
 * @param {Object} params - { page, page_size }
 */
export function getGradeRecords(params) {
  return api.get('/teacher/grade/records', { params })
}

/**
 * 获取成绩详情
 * @param {number} recordId - 成绩记录ID
 */
export function getGradeDetail(recordId) {
  return api.get(`/teacher/grade/records/${recordId}`)
}

/**
 * 获取AI分析报告
 * @param {number} recordId - 成绩记录ID
 * @param {boolean} regenerate - 是否重新生成
 */
export function getGradeReport(recordId, regenerate = false) {
  return api.get(`/teacher/grade/records/${recordId}/report`, {
    params: { regenerate }
  })
}

/**
 * 删除成绩记录
 * @param {number} recordId - 成绩记录ID
 */
export function deleteGradeRecord(recordId) {
  return api.delete(`/teacher/grade/records/${recordId}`)
}

/**
 * 导出成绩Excel
 * @param {number} recordId - 成绩记录ID
 * @returns {Blob} Excel文件blob
 */
export function exportGradeExcel(recordId) {
  return api.get(`/teacher/grade/records/${recordId}/export`, {
    responseType: 'arraybuffer'
  })
}
