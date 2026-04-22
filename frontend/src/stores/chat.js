import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  sendMessage as apiSendMessage,
  sendVoice as apiSendVoice,
  textToSpeech as apiTextToSpeech,
  getConversations as apiGetConversations,
  getConversationHistory as apiGetConversationHistory,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation
} from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([])
  const currentConvId = ref(null)
  const mode = ref('normal') // normal / emotion
  const currentEmotion = ref(0) // 0-5, 0=开心, 5=悲伤
  const isAITyping = ref(false)
  const conversations = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Emotion labels matching EmotionToggle component
  const emotionLabels = ['开心', '愉悦', '平静', '思考', '烦恼', '悲伤']
  const emotionEmojis = ['😄', '😊', '😌', '🤔', '😟', '😢']

  // Computed
  const currentEmotionLabel = computed(() => emotionLabels[currentEmotion.value] || '平静')
  const currentEmotionEmoji = computed(() => emotionEmojis[currentEmotion.value] || '😌')

  // Add a message to the chat
  function addMessage(message, isUser = false) {
    messages.value.push({
      id: Date.now(),
      content: message,
      isUser,
      timestamp: new Date().toISOString()
    })
    console.log('[ChatStore] Message added:', { isUser, messageLength: message.length })
  }

  // Set AI typing state
  function setAITyping(typing) {
    isAITyping.value = typing
    console.log('[ChatStore] AI typing state:', typing)
  }

  // Set emotion (0-5)
  function setEmotion(emotion) {
    currentEmotion.value = Math.max(0, Math.min(5, emotion))
    console.log('[ChatStore] Emotion set to:', currentEmotion.value)
  }

  // Toggle between normal and emotion mode
  function toggleMode() {
    mode.value = mode.value === 'normal' ? 'emotion' : 'normal'
    console.log('[ChatStore] Mode toggled to:', mode.value)
  }

  // Clear all messages
  function clearMessages() {
    messages.value = []
    console.log('[ChatStore] Messages cleared')
  }

  // Send text message
  async function sendMessage(content) {
    if (!content?.trim()) {
      console.warn('[ChatStore] Empty message, skipping')
      return
    }

    console.log('[ChatStore] Sending message:', content.substring(0, 50) + '...')
    loading.value = true
    error.value = null

    try {
      // Add user message to UI immediately
      addMessage(content, true)

      // Set AI typing indicator
      setAITyping(true)

      const response = await apiSendMessage({
        conv_id: currentConvId.value,
        message: content.trim(),
        mode: mode.value
      })

      console.log('[ChatStore] API response received:', response.data)

      // Add AI response
      const aiContent = response.data?.data?.content || response.data?.content || '抱歉，我没有收到有效的回复'
      addMessage(aiContent, false)

      return response.data
    } catch (err) {
      console.error('[ChatStore] Send message error:', err)
      error.value = err.message || '发送消息失败'
      // Add error message to chat
      addMessage('抱歉，发送消息失败了，请稍后重试', false)
      throw err
    } finally {
      loading.value = false
      setAITyping(false)
    }
  }

  // Send voice message - 语音识别（只返回文字）
  async function sendVoice(audioBlob) {
    console.log('[ChatStore] Sending voice for recognition, blob size:', audioBlob?.size)

    if (!audioBlob) {
      console.warn('[ChatStore] No audio blob provided')
      return null
    }

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      const response = await apiSendVoice(formData)
      console.log('[ChatStore] Voice recognition response:', response.data)

      // 返回识别出的文字
      const text = response.data?.data?.text || response.data?.text || ''
      return text
    } catch (err) {
      console.error('[ChatStore] Voice recognition error:', err)
      error.value = err.message || '语音识别失败'
      throw err
    }
  }

  // Text to Speech - 将文字转为语音播放
  async function speakText(text, voice = 'x4_lingxiaoyao_em') {
    console.log('[ChatStore] Requesting TTS, text length:', text.length)

    if (!text || !text.trim()) {
      console.warn('[ChatStore] Empty text for TTS')
      return null
    }

    try {
      const response = await apiTextToSpeech(text, voice)
      console.log('[ChatStore] TTS response:', response.data)

      // 返回音频URL
      const audioUrl = response.data?.data?.audio_url || response.data?.audio_url || ''
      return audioUrl
    } catch (err) {
      console.error('[ChatStore] TTS error:', err)
      error.value = err.message || '语音合成失败'
      throw err
    }
  }

  // Fetch conversations list
  async function fetchConversations() {
    console.log('[ChatStore] Fetching conversations')
    loading.value = true

    try {
      const response = await apiGetConversations()
      conversations.value = response.data?.data || []
      console.log('[ChatStore] Conversations loaded:', conversations.value.length)
      return conversations.value
    } catch (err) {
      console.error('[ChatStore] Fetch conversations error:', err)
      error.value = err.message || '获取会话列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch conversation history
  async function fetchConversationHistory(convId) {
    console.log('[ChatStore] Fetching conversation history:', convId)
    loading.value = true

    try {
      const response = await apiGetConversationHistory(convId)
      const history = response.data?.data || []

      // Set as current conversation and load messages
      currentConvId.value = convId
      messages.value = history.map((msg, index) => ({
        id: msg.id || index,
        content: msg.content,
        isUser: msg.role === 'user',
        timestamp: msg.timestamp || new Date().toISOString()
      }))

      console.log('[ChatStore] History loaded, messages:', messages.value.length)
      return messages.value
    } catch (err) {
      console.error('[ChatStore] Fetch history error:', err)
      error.value = err.message || '获取会话历史失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create new conversation
  async function createConversation(title = '新对话') {
    console.log('[ChatStore] Creating new conversation:', title)

    try {
      const response = await apiCreateConversation({ title })
      const conv = response.data?.data

      if (conv) {
        conversations.value.unshift(conv)
        currentConvId.value = conv.id
        clearMessages()
        console.log('[ChatStore] Conversation created:', conv.id)
      }

      return conv
    } catch (err) {
      console.error('[ChatStore] Create conversation error:', err)
      error.value = err.message || '创建会话失败'
      throw err
    }
  }

  // Delete conversation
  async function deleteConversation(convId) {
    console.log('[ChatStore] Deleting conversation:', convId)

    try {
      await apiDeleteConversation(convId)
      conversations.value = conversations.value.filter(c => c.id !== convId)

      // If deleted current conversation, clear it
      if (currentConvId.value === convId) {
        currentConvId.value = null
        clearMessages()
      }

      console.log('[ChatStore] Conversation deleted')
    } catch (err) {
      console.error('[ChatStore] Delete conversation error:', err)
      error.value = err.message || '删除会话失败'
      throw err
    }
  }

  // Start new chat (create conversation and clear messages)
  async function startNewChat() {
    await createConversation()
  }

  return {
    // State
    messages,
    currentConvId,
    mode,
    currentEmotion,
    isAITyping,
    conversations,
    loading,
    error,

    // Computed
    currentEmotionLabel,
    currentEmotionEmoji,

    // Actions
    addMessage,
    setAITyping,
    setEmotion,
    toggleMode,
    clearMessages,
    sendMessage,
    sendVoice,
    speakText,
    fetchConversations,
    fetchConversationHistory,
    createConversation,
    deleteConversation,
    startNewChat
  }
})
