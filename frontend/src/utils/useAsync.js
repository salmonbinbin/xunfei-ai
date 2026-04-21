import { ref } from 'vue'
import { handleError } from './errorHandler'

/**
 * 异步操作封装 Hook
 */
export function useAsync(asyncFn, options = {}) {
  const { immediate = false, onSuccess = null, onError = null } = options

  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function execute(...args) {
    loading.value = true
    error.value = null

    try {
      const result = await asyncFn(...args)
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      error.value = e
      handleError(e, { showMessage: true })
      onError?.(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    execute()
  }

  return {
    data,
    loading,
    error,
    execute
  }
}
