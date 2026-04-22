import api from './index'

/**
 * 发送文字消息
 * @param {Object} data - 消息数据
 * @param {string} data.conv_id - 会话ID
 * @param {string} data.message - 消息内容
 * @param {string} data.mode - 模式: normal / emotion
 * @returns {Promise}
 */
export function sendMessage({ conv_id, message, mode = 'normal' }) {
  console.log('[Chat API] Sending text message:', { conv_id, message, mode })
  return api.post('/chat/message', { conv_id, message, mode })
}

/**
 * 发送语音消息 - 语音识别（只返回文字，不发AI回复）
 * @param {FormData} formData - 包含audio文件
 * @returns {Promise}
 */
export function sendVoice(formData) {
  console.log('[Chat API] Sending voice for recognition')
  return api.post('/chat/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 语音合成 - 将文字转为语音
 * @param {string} text - 要转换的文字
 * @param {string} voice - 发音人，默认x4_lingxiaoyao_em
 * @returns {Promise}
 */
export function textToSpeech(text, voice = 'x4_lingxiaoyao_em') {
  console.log('[Chat API] Requesting TTS, text length:', text.length)
  return api.post('/chat/tts', null, {
    params: { text, voice }
  })
}

/**
 * 获取会话列表
 * @returns {Promise}
 */
export function getConversations() {
  console.log('[Chat API] Fetching conversations list')
  return api.get('/chat/conversations')
}

/**
 * 获取会话历史
 * @param {string} convId - 会话ID
 * @returns {Promise}
 */
export function getConversationHistory(convId) {
  console.log('[Chat API] Fetching conversation history:', convId)
  return api.get(`/chat/conversations/${convId}`)
}

/**
 * 创建新会话
 * @param {Object} data - 会话数据
 * @param {string} data.title - 会话标题
 * @returns {Promise}
 */
export function createConversation(data) {
  console.log('[Chat API] Creating new conversation:', data)
  return api.post('/chat/conversations', data)
}

/**
 * 删除会话
 * @param {string} convId - 会话ID
 * @returns {Promise}
 */
export function deleteConversation(convId) {
  console.log('[Chat API] Deleting conversation:', convId)
  return api.delete(`/chat/conversations/${convId}`)
}
