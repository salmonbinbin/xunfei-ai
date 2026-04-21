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
        <div v-if="messages.length === 0" class="empty-state">
          <div class="ai-avatar">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="24" fill="url(#aiGradient2Fresh)"/>
              <path d="M16 20C16 16.6863 18.6863 14 22 14C25.3137 14 28 16.6863 28 20V22H22C18.6863 22 16 24.6863 16 28V34H32V28C32 24.6863 29.3137 22 26 22C22.6863 22 20 24.6863 20 28V32H16V20Z" fill="#1E293B"/>
              <defs>
                <linearGradient id="aiGradient2Fresh" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#0891B2"/>
                  <stop offset="1" stop-color="#22D3EE"/>
                </linearGradient>
              </defs>
            </svg>
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
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div class="message-avatar">
            <div v-if="msg.role === 'user'" class="user-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div v-else class="ai-avatar-small">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              </svg>
            </div>
          </div>
          <div class="message-bubble">
            <p>{{ msg.content }}</p>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <div class="ai-avatar-small">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              </svg>
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
          <input
            v-model="inputMessage"
            type="text"
            class="chat-input"
            placeholder="输入消息..."
            @keyup.enter="sendMessage"
            :disabled="loading"
          />
          <button class="voice-btn" @click="toggleVoice">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </button>
          <button
            class="send-btn"
            @click="sendMessage"
            :disabled="loading || !inputMessage.trim()"
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
import { ref, nextTick } from 'vue'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

function addMessage(role, content) {
  messages.value.push({ role, content })
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || loading.value) return

  inputMessage.value = ''
  addMessage('user', text)
  loading.value = true

  setTimeout(() => {
    addMessage('assistant', '功能开发中，请连接后端API进行测试...')
    loading.value = false
  }, 1000)
}

function toggleVoice() {
  alert('语音功能开发中...')
}

function quickAsk(question) {
  inputMessage.value = question
  sendMessage()
}
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
  margin-bottom: 20px;
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
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  display: flex;
  align-items: center;
  justify-content: center;
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
  background: rgba(8, 145, 178, 0.1);
  border-color: rgba(8, 145, 178, 0.15);
  border-top-left-radius: 16px;
  border-top-right-radius: 4px;
}

.message-bubble p {
  color: #475569;
  font-size: 15px;
  line-height: 1.5;
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
  align-items: center;
}

.chat-input {
  flex: 1;
  padding: 14px 18px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  color: #1E293B;
  font-size: 15px;
  transition: all 0.2s ease;
}

.chat-input:focus {
  outline: none;
  border-color: #0891B2;
  box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
}

.chat-input::placeholder {
  color: #CBD5E1;
}

.voice-btn,
.send-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.voice-btn {
  background: rgba(8, 145, 178, 0.08);
  border: 1px solid rgba(8, 145, 178, 0.15);
  color: #64748B;
}

.voice-btn:hover {
  background: rgba(8, 145, 178, 0.12);
  color: #0891B2;
}

.send-btn {
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
}
</style>
