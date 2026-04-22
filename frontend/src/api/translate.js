import api from '@/api/index'

/**
 * 即时翻译
 * @param {string} text - 要翻译的文本
 * @param {string} sourceLang - 源语言代码
 * @param {string} targetLang - 目标语言代码
 * @returns {Promise<{translated_text: string, source_lang: string, target_lang: string}>}
 */
export function translateText(text, sourceLang, targetLang) {
  const formData = new FormData()
  formData.append('text', text)
  formData.append('source_lang', sourceLang)
  formData.append('target_lang', targetLang)
  return api.post('/translate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 文档翻译上传
 * @param {File} file - 要翻译的文件
 * @param {string} targetLang - 目标语言代码
 * @returns {Promise<{task_id: string, status: string}>}
 */
export function translateDocx(file, targetLang) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('target_lang', targetLang)
  return api.post('/translate/docx', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取翻译预览
 * @param {string} taskId - 任务ID
 * @returns {Promise<{task_id: string, status: string, translated_content: string, word_count: number}>}
 */
export function getTranslationPreview(taskId) {
  return api.get(`/translate/preview/${taskId}`)
}

/**
 * 下载翻译文档
 * @param {string} taskId - 任务ID
 * @returns {Promise<Blob>} 文件流
 */
export function downloadTranslation(taskId) {
  return api.get(`/translate/download/${taskId}`, {
    responseType: 'blob'
  })
}