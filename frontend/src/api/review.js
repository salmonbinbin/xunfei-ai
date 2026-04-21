import api from '@/api'

/**
 * 获取录音回顾列表
 * @param {Object} params - 查询参数
 * @param {string} params.status - 状态筛选 (pending/processing/completed)
 * @param {string} params.record_type - 类型筛选 (course/meeting)
 * @param {number} params.skip - 偏移量
 * @param {number} params.limit - 获取数量
 * @returns {Promise<{data: Array}>}
 */
export function getReviewList(params = {}) {
  return api.get('/review', { params })
}

/**
 * 获取录音回顾详情
 * @param {number} reviewId - 回顾ID
 * @returns {Promise<{data: Object}>}
 */
export function getReviewDetail(reviewId) {
  return api.get(`/review/${reviewId}`)
}

/**
 * 上传录音文件
 * @param {File} audioFile - 音频文件 (MP3, ≤50MB)
 * @param {Object} options - 上传选项
 * @param {string} options.record_type - 录音类型 (course/meeting)
 * @param {string} options.title - 标题 (可选)
 * @param {string} options.language - 语言 (mandarin/cantonese/english, 默认 mandarin)
 * @param {Function} options.onProgress - 进度回调
 * @returns {Promise<{data: {record_id: number, message: string, status: string}}>}
 */
export function uploadAudio(audioFile, options = {}) {
  const { record_type = 'course', title = '', language = 'mandarin', onProgress = null } = options

  const formData = new FormData()
  formData.append('record_type', record_type)
  formData.append('language', language)
  if (title) {
    formData.append('title', title)
  }
  formData.append('audio', audioFile)

  const config = {
    headers: { 'Content-Type': 'multipart/form-data' }
  }

  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      onProgress(percent)
    }
  }

  return api.post('/review/upload', formData, config)
}

/**
 * 获取转写结果
 * @param {number} reviewId - 回顾ID
 * @returns {Promise<{data: Object}>}
 */
export function getTranscription(reviewId) {
  return api.get(`/review/${reviewId}/transcription`)
}

/**
 * 获取总结结果
 * @param {number} reviewId - 回顾ID
 * @returns {Promise<{data: Object}>}
 */
export function getSummary(reviewId) {
  return api.get(`/review/${reviewId}/summary`)
}

/**
 * 删除录音回顾
 * @param {number} reviewId - 回顾ID
 * @returns {Promise<{success: boolean}>}
 */
export function deleteReview(reviewId) {
  return api.delete(`/review/${reviewId}`)
}

/**
 * 重新生成AI摘要
 * @param {number} reviewId - 回顾ID
 * @returns {Promise<{success: boolean, message: string, summary_id: number}>}
 */
export function regenerateSummary(reviewId) {
  return api.post(`/review/${reviewId}/regenerate-summary`)
}

/**
 * 导出为Word文档
 * @param {number} summaryId - 总结ID
 * @returns {Promise<Blob>} 文件流
 */
export function exportToDocx(summaryId) {
  return api.post(`/export/docx`, { summary_id: summaryId }, {
    responseType: 'blob'
  })
}

/**
 * 导出为PPT
 * @param {number} summaryId - 总结ID
 * @returns {Promise<Blob>} 文件流
 */
export function exportToPptx(summaryId) {
  return api.post(`/export/pptx`, { summary_id: summaryId }, {
    responseType: 'blob'
  })
}

/**
 * 下载文件
 * @param {Blob} blob - 文件数据
 * @param {string} filename - 文件名
 */
export function downloadFile(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}