<template>
  <div class="ai-sister-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI学姐</h1>
        <p class="page-subtitle">有什么想聊的？我在这里帮助你</p>
      </div>
    </div>

    <!-- 对话容器 -->
    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 空状态 -->
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <div class="ai-avatar">
            <img src="/images/sisiter-avatar.jpg" alt="AI学姐" class="sister-avatar" />
          </div>
          <p class="empty-greeting">你好，同学！我是AI学姐</p>
          <p class="empty-hint">可以问我关于校园的问题，或者聊聊学习生活中的事情~</p>
          <div class="quick-questions">
            <button class="quick-btn" @click="quickAsk('图书馆开放时间？')">图书馆开放时间？</button>
            <button class="quick-btn" @click="quickAsk('如何申请调课？')">如何申请调课？</button>
            <button class="quick-btn" @click="quickAsk('9教是指哪栋楼？')">9教是指哪栋楼？</button>
          </div>
        </div>

        <!-- 消息 -->
        <div
          v-for="(msg, index) in chatStore.messages"
          :key="index"
          :class="['message', msg.isUser ? 'user' : 'assistant']"
        >
          <div class="message-avatar">
            <div v-if="msg.isUser" class="user-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div v-else class="ai-avatar-small">
              <img src="/images/sisiter-avatar.jpg" alt="AI学姐" class="sister-avatar-small" />
            </div>
          </div>
          <div class="message-bubble">
            <p>{{ msg.content }}</p>
            <div class="message-actions" v-if="!msg.isUser">
              <!-- 语音播放按钮 -->
              <button
                class="play-btn"
                @click="playMessage(msg)"
                :class="{ playing: msg.isPlaying, paused: msg.isPaused }"
              >
                <!-- 播放中显示暂停图标，停止时显示播放图标 -->
                <svg v-if="msg.isPlaying" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16"/>
                  <rect x="14" y="4" width="4" height="16"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
              </button>
            </div>
            <span v-if="!msg.isUser" class="message-time">{{ formatTime(msg.timestamp) }}</span>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="chatStore.isAITyping" class="message assistant">
          <div class="message-avatar">
            <div class="ai-avatar-small">
              <img src="/images/sisiter-avatar.jpg" alt="AI学姐" class="sister-avatar-small" />
            </div>
          </div>
          <div class="message-bubble loading">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            ref="textareaRef"
            v-model="inputMessage"
            class="chat-textarea"
            placeholder="输入消息..."
            rows="1"
            @keydown.enter.exact.prevent="handleEnterKey"
            @input="autoResizeTextarea"
            :disabled="chatStore.loading"
          ></textarea>

          <!-- 语音输入按钮 -->
          <VoiceInput
            class="voice-btn"
            @transcript="handleVoiceTranscript"
            @error="handleVoiceError"
          />

          <!-- 发送按钮 -->
          <button
            class="send-btn"
            @click="handleSendMessage"
            :disabled="chatStore.loading || !inputMessage.trim()"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import VoiceInput from '@/components/VoiceInput.vue'

// Store
const chatStore = useChatStore()

// Refs
const messagesContainer = ref(null)
const textareaRef = ref(null)
const inputMessage = ref('')

// Format timestamp to readable time
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// Scroll to bottom of messages
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      console.log('[AISister] Scrolled to bottom, scrollTop:', messagesContainer.value.scrollTop)
    }
  })
}

// Auto-resize textarea height
function autoResizeTextarea() {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 120) + 'px'
  }
}

// Handle Enter key (without Shift)
function handleEnterKey(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSendMessage()
  }
}

// Handle send message
async function handleSendMessage() {
  const text = inputMessage.value.trim()
  if (!text || chatStore.loading) {
    console.log('[AISister] Cannot send: empty or loading')
    return
  }

  console.log('[AISister] Sending message:', text.substring(0, 50) + '...')
  inputMessage.value = ''

  // Reset textarea height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }

  try {
    await chatStore.sendMessage(text)
    scrollToBottom()
  } catch (error) {
    console.error('[AISister] Send message error:', error)
  }
}

// Handle quick ask buttons
function quickAsk(question) {
  console.log('[AISister] Quick ask:', question)
  inputMessage.value = question
  handleSendMessage()
}

// Handle voice transcript from VoiceInput
async function handleVoiceTranscript(data) {
  console.log('[AISister] Voice data received:', data)

  if (!data) return

  // Handle audio blob from VoiceInput
  if (data.type === 'audio' && data.blob) {
    console.log('[AISister] Processing audio blob, size:', data.blob.size, 'bytes')

    try {
      // 调用语音识别，只返回文字
      const text = await chatStore.sendVoice(data.blob)
      console.log('[AISister] Recognized text:', text)

      if (text && text.trim()) {
        // 将识别文字填入输入框
        inputMessage.value = text
        await nextTick()
        // 自动聚焦到输入框
        textareaRef.value?.focus()
      } else {
        console.warn('[AISister] No text recognized from voice')
      }
    } catch (error) {
      console.error('[AISister] Voice recognition error:', error)
    }
    return
  }

  // Handle text transcript (for future ASR integration)
  if (typeof data === 'string' && data.trim()) {
    inputMessage.value = data
    await nextTick()
    handleSendMessage()
  }
}

// Play message with TTS (supporting pause/resume)
async function playMessage(msg) {
  if (!msg.content) return

  console.log('[AISister] Play message, isPlaying:', msg.isPlaying, 'hasAudio:', !!msg.audio)

  // 如果已经有音频对象，处理暂停/继续
  if (msg.audio) {
    if (msg.isPlaying) {
      // 暂停播放
      msg.audio.pause()
      msg.isPlaying = false
      msg.isPaused = true
      console.log('[AISister] TTS playback paused')
    } else {
      // 继续播放
      msg.audio.play()
      msg.isPlaying = true
      msg.isPaused = false
      console.log('[AISister] TTS playback resumed')
    }
    return
  }

  // 没有音频对象，创建新的
  console.log('[AISister] Playing message:', msg.content.substring(0, 50))

  try {
    // 获取TTS音频URL
    const audioUrl = await chatStore.speakText(msg.content)
    console.log('[AISister] TTS audio URL:', audioUrl)

    if (audioUrl) {
      // 创建音频播放器
      const audio = new Audio(audioUrl)
      msg.audio = audio
      msg.isPlaying = true
      msg.isPaused = false

      audio.onended = () => {
        msg.isPlaying = false
        msg.isPaused = false
        msg.audio = null
        console.log('[AISister] TTS playback ended')
      }
      audio.onerror = (e) => {
        console.error('[AISister] TTS playback error:', e)
        msg.isPlaying = false
        msg.isPaused = false
        msg.audio = null
      }
      await audio.play()
      console.log('[AISister] TTS playback started')
    } else {
      msg.isPlaying = false
    }
  } catch (error) {
    console.error('[AISister] TTS error:', error)
    msg.isPlaying = false
    msg.audio = null
  }
}

// Handle voice input error
function handleVoiceError(error) {
  console.error('[AISister] Voice input error:', error)
}

// On mount, start a new conversation
onMounted(() => {
  console.log('[AISister] Component mounted')
  scrollToBottom()
})
</script>

<style scoped>
.ai-sister-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: #F8FAFC;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 15px;
  color: #64748B;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.ai-avatar {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
}

.sister-avatar {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: 50%;
}

.sister-avatar-small {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 50%;
}

.empty-greeting {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: #64748B;
  margin-bottom: 24px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-btn {
  padding: 10px 18px;
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  border-radius: 20px;
  color: #0891B2;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-btn:hover {
  background: rgba(8, 145, 178, 0.12);
  border-color: rgba(8, 145, 178, 0.25);
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(8, 145, 178, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
}

.ai-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
}

.message-bubble {
  max-width: 70%;
  padding: 14px 18px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  border-top-left-radius: 4px;
}

.message.user .message-bubble {
  background: rgba(8, 145, 178, 0.08);
  border-color: rgba(8, 145, 178, 0.12);
  border-top-left-radius: 16px;
  border-top-right-radius: 4px;
}

.message-bubble p {
  color: #475569;
  font-size: 15px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #CBD5E1;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.play-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(8, 145, 178, 0.1);
  border: 1px solid rgba(8, 145, 178, 0.2);
  color: #0891B2;
  cursor: pointer;
  transition: all 0.2s ease;
}

.play-btn:hover {
  background: rgba(8, 145, 178, 0.2);
  border-color: rgba(8, 145, 178, 0.3);
}

.play-btn.playing {
  background: rgba(8, 145, 178, 0.25);
  color: #0891B2;
}

.play-btn.paused {
  background: rgba(8, 145, 178, 0.15);
  color: #0891B2;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0891B2;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  padding: 16px 20px;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-textarea {
  flex: 1;
  padding: 14px 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  color: #1E293B;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  transition: all 0.2s ease;
  min-height: 48px;
  max-height: 120px;
  line-height: 1.5;
}

.chat-textarea:focus {
  outline: none;
  border-color: #0891B2;
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
}

.chat-textarea::placeholder {
  color: #CBD5E1;
}

.chat-textarea:disabled {
  background: #F8FAFC;
  cursor: not-allowed;
}

.voice-btn {
  flex-shrink: 0;
}

.send-btn {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  color: white;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .ai-sister-page {
    padding: 16px;
    height: calc(100vh - 100px);
  }

  .page-title {
    font-size: 24px;
  }

  .message-bubble {
    max-width: 85%;
  }

  .quick-questions {
    flex-direction: column;
  }

  .quick-btn {
    width: 100%;
  }
}
</style>
