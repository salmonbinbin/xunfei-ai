import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isLoading = ref(false)
  const loadingText = ref('')
  const deviceType = ref('desktop') // 'desktop', 'tablet', 'mobile'

  function setLoading(loading, text = '') {
    isLoading.value = loading
    loadingText.value = text
  }

  function setDeviceType(type) {
    deviceType.value = type
  }

  function detectDevice() {
    const width = window.innerWidth
    if (width < 768) {
      deviceType.value = 'mobile'
    } else if (width < 1024) {
      deviceType.value = 'tablet'
    } else {
      deviceType.value = 'desktop'
    }
  }

  return {
    isLoading,
    loadingText,
    deviceType,
    setLoading,
    setDeviceType,
    detectDevice
  }
})
