import { ElMessage } from 'element-plus'

/**
 * 统一错误处理函数
 * @param {Error} error - 错误对象
 * @param {Object} options - 配置选项
 */
export function handleError(error, options = {}) {
  const { showMessage = true, fallbackMessage = '操作失败，请稍后重试' } = options

  if (import.meta.env.DEV) {
    console.error('[Error]', error)
  }

  if (showMessage) {
    const message = error?.response?.data?.error?.message || error.message || fallbackMessage
    ElMessage.error({
      message,
      duration: 3000,
      showClose: true
    })
  }
}

/**
 * API 响应错误处理
 */
export function setupInterceptors(api) {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      const { response } = error

      if (response) {
        switch (response.status) {
          case 401:
            ElMessage.warning('登录已过期，请重新登录')
            break
          case 403:
            ElMessage.warning('没有权限执行此操作')
            break
          case 404:
            handleError(new Error('请求的资源不存在'), { showMessage: true })
            break
          case 422:
            const validationMsg = response.data?.error?.details
            ElMessage.warning(validationMsg || '数据验证失败')
            break
          case 502:
            handleError(new Error('第三方服务暂时不可用'), { showMessage: true })
            break
          default:
            handleError(error)
        }
      } else if (error.request) {
        ElMessage.error('网络连接失败，请检查网络')
      } else {
        handleError(error)
      }

      return Promise.reject(error)
    }
  )
}
