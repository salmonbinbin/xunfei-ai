import api from '@/api'

/**
 * 发送消息给AI学姐
 * @param {string} message - 用户消息
 * @param {number} emotion - 情感状态 (0-5)
 * @returns {Promise<{reply: string, emotion: number}>}
 */
export function sendMessage(message, emotion = 0) {
  return api.post('/chat', { message, emotion })
}

/**
 * 获取会话列表
 * @returns {Promise<Array>}
 */
export function getChatConversations() {
  return api.get('/chat/conversations')
}

/**
 * 获取聊天历史
 * @param {number} limit - 获取数量
 * @param {number} offset - 偏移量
 * @returns {Promise<{messages: Array}>}
 */
export function getChatHistory(limit = 50, offset = 0) {
  return api.get('/chat/history', { params: { limit, offset } })
}

/**
 * 清空聊天历史
 * @returns {Promise<{success: boolean}>}
 */
export function clearChatHistory() {
  return api.delete('/chat/history')
}

/**
 * 语音输入（讯飞ASR）
 * @param {Blob} audioFile - 音频文件
 * @returns {Promise<{text: string}>}
 */
export function speechToText(audioFile) {
  const formData = new FormData()
  formData.append('audio', audioFile)
  return api.post('/chat/asr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 文字转语音（讯飞TTS）
 * @param {string} text - 要转换的文字
 * @returns {Promise<{audio_url: string}>}
 */
export function textToSpeech(text) {
  return api.post('/chat/tts', { text })
}
