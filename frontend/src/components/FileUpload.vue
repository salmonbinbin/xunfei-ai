<template>
  <div
    class="file-upload relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300"
    :class="[
      isDragOver ? 'border-neon-purple bg-neon-purple/10' : 'border-neon-purple/30',
      { 'opacity-50 pointer-events-none': disabled }
    ]"
    @dragover.prevent="isDragOver = true"
    @dragleave.prevent="isDragOver = false"
    @drop.prevent="handleDrop"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      class="hidden"
      @change="handleFileSelect"
    />

    <div v-if="!previewUrl">
      <svg class="w-12 h-12 mx-auto mb-4 text-neon-purple/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="text-text-body mb-1">{{ label }}</p>
      <p class="text-xs text-text-secondary">{{ hint }}</p>
    </div>

    <div v-else class="preview-container">
      <img v-if="isImage" :src="previewUrl" class="max-h-40 mx-auto rounded-lg" />
      <div v-else class="flex items-center justify-center gap-2">
        <svg class="w-8 h-8 text-neon-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span class="text-sm text-text-body">{{ fileName }}</span>
      </div>
      <button
        @click.stop="removeFile"
        class="mt-3 px-3 py-1 text-xs text-neon-red hover:bg-neon-red/10 rounded-full transition-colors"
      >
        移除文件
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [File, Array],
    default: null
  },
  label: {
    type: String,
    default: '点击或拖拽文件到此处上传'
  },
  hint: {
    type: String,
    default: '支持图片、音频、文档'
  },
  accept: {
    type: String,
    default: '*'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const isDragOver = ref(false)
const previewUrl = ref(null)
const fileName = ref('')

const isImage = computed(() => {
  if (!props.modelValue) return false
  return props.modelValue.type?.startsWith('image/')
})

function triggerFileInput() {
  if (!props.disabled) {
    fileInput.value?.click()
  }
}

function handleFileSelect(event) {
  const files = event.target.files
  if (files?.length) {
    processFile(files[0])
  }
}

function handleDrop(event) {
  isDragOver.value = false
  const files = event.dataTransfer.files
  if (files?.length) {
    processFile(files[0])
  }
}

function processFile(file) {
  emit('update:modelValue', file)
  fileName.value = file.name

  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      previewUrl.value = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    previewUrl.value = 'file'
  }
}

function removeFile() {
  emit('update:modelValue', null)
  previewUrl.value = null
  fileName.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>
