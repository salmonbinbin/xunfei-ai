<template>
  <div class="emotion-toggle flex items-center gap-1">
    <button
      v-for="(label, index) in emotions"
      :key="index"
      @click="selectEmotion(index)"
      :class="[
        'w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all duration-300',
        currentEmotion === index
          ? 'bg-neon-purple text-white scale-110 shadow-neon-purple'
          : 'bg-secondary-bg text-text-secondary hover:bg-neon-purple/20'
      ]"
      :title="label"
    >
      {{ getEmoji(index) }}
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const emotions = ['开心', '愉悦', '平静', '思考', '烦恼', '悲伤']
const emotionEmojis = ['😄', '😊', '😌', '🤔', '😟', '😢']

const currentEmotion = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  currentEmotion.value = val
})

function selectEmotion(index) {
  currentEmotion.value = index
  emit('update:modelValue', index)
}

function getEmoji(index) {
  return emotionEmojis[index] || '😐'
}
</script>
