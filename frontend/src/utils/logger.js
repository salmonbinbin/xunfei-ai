/**
 * 前端日志工具
 * 生产环境只记录 warning 和 error
 */
const logger = {
  _isDev: import.meta.env.DEV,

  debug(...args) {
    if (this._isDev) {
      console.debug('[DEBUG]', ...args)
    }
  },

  info(...args) {
    if (this._isDev) {
      console.info('[INFO]', ...args)
    }
  },

  warn(...args) {
    console.warn('[WARN]', ...args)
  },

  error(...args) {
    console.error('[ERROR]', ...args)
  }
}

export default logger
