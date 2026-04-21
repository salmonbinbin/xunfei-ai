<template>
  <div class="voice-input relative">
    <button
      @click="toggleRecording"
      @mousedown="startRecording"
      @mouseup="stopRecording"
      @mouseleave="stopRecording"
      @touchstart.prevent="startRecording"
      @touchend.prevent="stopRecording"
      :class="[
        'w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300',
        isRecording ? 'bg-neon-red animate-pulse-glow' : 'glass-button'
      ]"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    </button>

    <div v-if="isRecording" class="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
      <span class="text-xs text-neon-red font-mono">Recording...</span>
    </div>

    <div v-if="transcript" class="mt-2 text-sm text-text-body">
      {{ transcript }}
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const emit = defineEmits(['transcript'])

const isRecording = ref(false)
const transcript = ref('')
let mediaRecorder = null
let audioChunks = []

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      // Here you would typically send the audio to your ASR API
      // For now, we'll just show the recording state
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.start()
    isRecording.value = true
  } catch (error) {
    console.error('Failed to start recording:', error)
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

onUnmounted(() => {
  if (mediaRecorder) {
    mediaRecorder.stop()
  }
})
</script>

<style scoped>
.animate-pulse-glow {
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(244, 63, 94, 0.5), 0 0 20px rgba(244, 63, 94, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(244, 63, 94, 0.8), 0 0 40px rgba(244, 63, 94, 0.5);
  }
}
</style>
