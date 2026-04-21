<template>
  <div class="ai-bubble flex gap-3" :class="{ 'flex-row-reverse': isUser }">
    <div
      :class="[
        'max-w-[80%] rounded-2xl px-4 py-3',
        isUser
          ? 'bg-gradient-to-br from-neon-purple to-neon-purple-light text-white rounded-br-sm'
          : 'glass-card rounded-bl-sm'
      ]"
    >
      <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ content }}</p>
      <div
        v-if="!isUser"
        class="mt-2 flex items-center gap-2"
      >
        <button
          @click="$emit('play')"
          class="p-1 rounded-full hover:bg-white/10 transition-colors"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>
        <span class="text-xs text-text-secondary">{{ time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  content: {
    type: String,
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  },
  time: {
    type: String,
    default: ''
  }
})

defineEmits(['play'])
</script>
