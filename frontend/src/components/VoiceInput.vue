<template>
  <div class="voice-input relative">
    <!-- 外圈动画 ring -->
    <div
      v-if="isRecording"
      class="absolute inset-0 rounded-full recording-ring"
    ></div>

    <!-- 主按钮 -->
    <button
      @click="toggleRecording"
      @mousedown.prevent="startRecording"
      @mouseup.prevent="stopRecording"
      @mouseleave="stopRecording"
      @touchstart.prevent="startRecording"
      @touchend.prevent="stopRecording"
      :class="[
        'voice-btn relative z-10 w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200',
        isRecording ? 'recording-active' : 'idle-state',
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      ]"
      :disabled="disabled"
    >
      <!-- 麦克风图标 -->
      <svg
        class="w-6 h-6 transition-all duration-200"
        :class="isRecording ? 'text-white scale-110' : 'text-cyan-600'"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
        />
      </svg>

      <!-- 录音中波纹动画 -->
      <span
        v-if="isRecording"
        class="absolute inset-0 rounded-full bg-cyan-500 opacity-20 animate-ping"
      ></span>
    </button>

    <!-- 状态文字 -->
    <div class="mt-3 text-center">
      <span
        v-if="isRecording"
        class="text-xs font-medium text-cyan-500 animate-pulse"
      >
        录音中...
      </span>
      <span
        v-else
        class="text-xs text-gray-400"
      >
        长按说话
      </span>
    </div>

    <!-- 短暂的成功提示 -->
    <Transition name="flash">
      <div
        v-if="showSuccess"
        class="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
      >
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const emit = defineEmits(['transcript', 'error'])

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const isRecording = ref(false)
const showSuccess = ref(false)
let mediaRecorder = null
let audioChunks = []
let stream = null

/**
 * Start recording audio
 */
async function startRecording() {
  if (props.disabled || isRecording.value) {
    console.log('[VoiceInput] Cannot start recording: disabled or already recording')
    return
  }

  try {
    console.log('[VoiceInput] Starting recording...')
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      console.log('[VoiceInput] Audio chunk available:', event.data.size, 'bytes')
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      console.log('[VoiceInput] Recording stopped, processing...')
      await processRecording()
    }

    mediaRecorder.onerror = (event) => {
      console.error('[VoiceInput] MediaRecorder error:', event.error)
      emit('error', { message: '录音失败: ' + event.error?.message })
      cleanup()
    }

    mediaRecorder.start(100)
    isRecording.value = true
    console.log('[VoiceInput] Recording started successfully')
  } catch (error) {
    console.error('[VoiceInput] Failed to start recording:', error)
    emit('error', { message: '无法访问麦克风，请检查权限设置' })
    cleanup()
  }
}

/**
 * Stop recording audio
 */
function stopRecording() {
  if (mediaRecorder && isRecording.value) {
    console.log('[VoiceInput] Stopping recording...')
    mediaRecorder.stop()
    isRecording.value = false
  }
}

/**
 * Process recorded audio blob
 */
async function processRecording() {
  if (audioChunks.length === 0) {
    console.warn('[VoiceInput] No audio chunks recorded')
    return
  }

  try {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
    console.log('[VoiceInput] Audio blob created, size:', audioBlob.size, 'bytes')

    emit('transcript', { type: 'audio', blob: audioBlob })

    // 显示成功提示
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 1500)

    audioChunks = []
    cleanup()
  } catch (error) {
    console.error('[VoiceInput] Error processing recording:', error)
    emit('error', { message: '处理录音失败' })
  }
}

/**
 * Cleanup media resources
 */
function cleanup() {
  if (stream) {
    stream.getTracks().forEach(track => {
      track.stop()
      console.log('[VoiceInput] Track stopped:', track.kind)
    })
    stream = null
  }
  mediaRecorder = null
}

/**
 * Toggle recording state
 */
function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

onUnmounted(() => {
  console.log('[VoiceInput] Component unmounting, cleanup...')
  cleanup()
})
</script>

<style scoped>
.voice-input {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
}

/* 闲置状态 */
.idle-state {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.15), rgba(34, 211, 238, 0.1));
  border: 2px solid rgba(8, 145, 178, 0.3);
  color: #0891B2;
  cursor: pointer;
  transition: all 0.3s ease;
}

.idle-state:hover {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.25), rgba(34, 211, 238, 0.2));
  border-color: rgba(8, 145, 178, 0.5);
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(8, 145, 178, 0.3);
}

.idle-state:active {
  transform: scale(0.95);
}

/* 录音中状态 */
.recording-active {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border: 2px solid #0891B2;
  color: white;
  cursor: pointer;
  box-shadow: 0 0 30px rgba(8, 145, 178, 0.6);
  animation: recording-pulse 1.5s ease-in-out infinite;
}

@keyframes recording-pulse {
  0%, 100% {
    box-shadow: 0 0 10px rgba(8, 145, 178, 0.5), 0 0 20px rgba(8, 145, 178, 0.3);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 25px rgba(8, 145, 178, 0.8), 0 0 50px rgba(34, 211, 238, 0.5);
    transform: scale(1.02);
  }
}

/* 外圈波纹 */
.recording-ring {
  pointer-events: none;
  border: 3px solid rgba(8, 145, 178, 0.5);
  animation: ring-expand 1.5s ease-out infinite;
}

@keyframes ring-expand {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

/* 麦克风波纹动画 */
.animate-ping {
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* 成功提示动画 */
.flash-enter-active {
  animation: flash-in 0.3s ease-out;
}

.flash-leave-active {
  animation: flash-out 0.3s ease-in;
}

@keyframes flash-in {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes flash-out {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}

button:disabled {
  cursor: not-allowed;
}
</style>
