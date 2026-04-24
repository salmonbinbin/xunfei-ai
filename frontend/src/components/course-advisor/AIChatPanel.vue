<template>
  <div class="ai-chat-panel">
    <div class="chat-header">
      <div class="chat-avatar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
      </div>
      <div class="chat-info">
        <span class="chat-title">选课小助手</span>
        <span class="chat-status">在线</span>
      </div>
    </div>

    <!-- 对话历史 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <p>你好！我是选课小助手，可以帮你：</p>
        <ul>
          <li>根据你的目标推荐合适的课程</li>
          <li>解答选课相关问题</li>
          <li>检测课程时间冲突</li>
        </ul>
        <p class="hint">试试发送："我想选一门对考研有帮助的数学课"</p>
      </div>

      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message"
        :class="msg.role"
      >
        <div class="message-content">{{ msg.content }}</div>
        <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="message assistant loading">
        <div class="message-content">
          <span class="loading-dots">
            <span></span><span></span><span></span>
          </span>
        </div>
      </div>
    </div>

    <!-- 推荐课程 -->
    <div v-if="recommendedCourses.length > 0" class="recommended-section">
      <div class="recommended-header">为你推荐</div>
      <div class="recommended-list">
        <div
          v-for="course in recommendedCourses"
          :key="course.id"
          class="recommended-item"
          @click="$emit('selectCourse', course)"
        >
          <span class="course-name">{{ course.name }}</span>
          <span class="course-reason">{{ course.match_reason || course.teacher }}</span>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="输入你的选课问题..."
        class="input-field"
        @keyup.enter="sendMessage"
        :disabled="loading"
      />
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="!inputMessage.trim() || loading"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  recommendedCourses: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send', 'selectCourse'])

const inputMessage = ref('')
const messagesContainer = ref(null)

function sendMessage() {
  const message = inputMessage.value.trim()
  if (!message) return

  emit('send', message)
  inputMessage.value = ''
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
watch(() => props.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})
</script>

<style scoped>
.ai-chat-panel {
  display: flex;
  flex-direction: column;
  height: 400px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  color: #fff;
}

.chat-avatar {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-info {
  display: flex;
  flex-direction: column;
}

.chat-title {
  font-size: 14px;
  font-weight: 600;
}

.chat-status {
  font-size: 11px;
  opacity: 0.8;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #64748B;
}

.empty-state p {
  margin-bottom: 12px;
}

.empty-state ul {
  text-align: left;
  padding-left: 20px;
  font-size: 13px;
}

.empty-state li {
  margin-bottom: 6px;
}

.empty-state .hint {
  margin-top: 16px;
  font-size: 12px;
  color: #0891B2;
  background: rgba(8, 145, 178, 0.08);
  padding: 8px 12px;
  border-radius: 8px;
}

.message {
  margin-bottom: 12px;
}

.message.user {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message.assistant {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-content {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
}

.message.user .message-content {
  background: #0891B2;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: #F1F5F9;
  color: #1E293B;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 10px;
  color: #94A3B8;
  margin-top: 4px;
}

.message.loading .message-content {
  display: flex;
  align-items: center;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #94A3B8;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.recommended-section {
  padding: 12px 16px;
  border-top: 1px solid #F1F5F9;
  background: #F8FAFC;
}

.recommended-header {
  font-size: 12px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 8px;
}

.recommended-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.recommended-item {
  flex-shrink: 0;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recommended-item:hover {
  border-color: #0891B2;
  background: rgba(8, 145, 178, 0.03);
}

.course-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #1E293B;
}

.course-reason {
  display: block;
  font-size: 11px;
  color: #64748B;
  margin-top: 2px;
}

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #F1F5F9;
}

.input-field {
  flex: 1;
  padding: 10px 14px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-size: 14px;
  color: #1E293B;
}

.input-field:focus {
  outline: none;
  border-color: #0891B2;
}

.input-field::placeholder {
  color: #94A3B8;
}

.send-btn {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.25);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>