import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const currentEmotion = ref(0) // 0-5, 0=开心, 5=悲伤
  const isAITyping = ref(false)

  const emotionLabels = ['开心', '愉悦', '平静', '思考', '烦恼', '悲伤']

  function addMessage(message, isUser = false) {
    messages.value.push({
      id: Date.now(),
      content: message,
      isUser,
      timestamp: new Date().toISOString()
    })
  }

  function setAITyping(typing) {
    isAITyping.value = typing
  }

  function setEmotion(emotion) {
    currentEmotion.value = Math.max(0, Math.min(5, emotion))
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    currentEmotion,
    isAITyping,
    emotionLabels,
    addMessage,
    setAITyping,
    setEmotion,
    clearMessages
  }
})
