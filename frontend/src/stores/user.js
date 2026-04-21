import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, updateProfile as updateProfileApi, getCurrentUser } from '@/api/auth'
import logger from '@/utils/logger'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const hasProfile = computed(() => {
    // 优先使用 login/register 返回的 has_profile 标志
    if (userInfo.value?.has_profile !== undefined) {
      return userInfo.value.has_profile
    }
    // 如果 userInfo 有 profile 数据也检查
    return !!(userInfo.value?.profile?.major && userInfo.value?.profile?.grade)
  })

  async function login(credentials) {
    loading.value = true
    try {
      const { data } = await loginApi(credentials)
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      userInfo.value = data.user
      logger.info('[UserStore] Login successful, token saved')
      return data
    } catch (error) {
      logger.error('[UserStore] Login failed:', error.message || error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function register(credentials) {
    loading.value = true
    try {
      const { data } = await registerApi(credentials)
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      userInfo.value = data.user
      logger.info('[UserStore] Register successful, token saved')
      return data
    } catch (error) {
      logger.error('[UserStore] Register failed:', error.message || error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return null
    loading.value = true
    try {
      const { data } = await getCurrentUser()
      userInfo.value = data
      return data
    } catch (error) {
      logger.error('[UserStore] Failed to fetch user:', error.message || error)
      logout()
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(profileData) {
    loading.value = true
    try {
      await updateProfileApi(profileData)
      await fetchUser()
      logger.info('[UserStore] Profile updated successfully')
    } catch (error) {
      logger.error('[UserStore] Profile update failed:', error.message || error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    logger.info('[UserStore] User logged out')
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    hasProfile,
    login,
    register,
    fetchUser,
    updateProfile,
    logout
  }
})