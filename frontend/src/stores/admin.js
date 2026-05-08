import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminLogin, adminLogout, getAdminProfile } from '@/api/admin/auth'
import logger from '@/utils/logger'

export const useAdminStore = defineStore('admin', () => {
  // State
  const token = ref(localStorage.getItem('admin_token') || '')
  const adminInfo = ref(null)
  const loading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isSuperAdmin = computed(() => adminInfo.value?.role === 'super_admin')
  const isAuditor = computed(() => adminInfo.value?.role === 'auditor')

  // Actions
  async function login(username, password) {
    loading.value = true
    logger.info('[AdminStore] Login attempt:', { username })
    try {
      const res = await adminLogin(username, password)
      token.value = res.data?.data?.token || res.data?.token
      adminInfo.value = res.data?.data?.admin || res.data?.admin
      localStorage.setItem('admin_token', token.value)
      logger.info('[AdminStore] Login successful, admin:', adminInfo.value?.username)
      return res.data
    } catch (error) {
      logger.error('[AdminStore] Login failed:', error?.response?.data || error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    logger.info('[AdminStore] Logout attempt')
    try {
      await adminLogout()
      logger.info('[AdminStore] Logout successful')
    } catch (error) {
      logger.warn('[AdminStore] Logout API failed, clearing local state:', error.message)
    } finally {
      token.value = ''
      adminInfo.value = null
      localStorage.removeItem('admin_token')
      loading.value = false
    }
  }

  async function fetchProfile() {
    if (!token.value) {
      logger.debug('[AdminStore] No token, skipping profile fetch')
      return null
    }
    loading.value = true
    logger.debug('[AdminStore] Fetching admin profile')
    try {
      const res = await getAdminProfile()
      adminInfo.value = res.data?.data || res.data
      logger.info('[AdminStore] Profile fetched:', adminInfo.value?.username)
      return adminInfo.value
    } catch (error) {
      logger.error('[AdminStore] Failed to fetch profile:', error?.response?.data || error.message)
      // Token might be invalid
      if (error?.response?.status === 401) {
        token.value = ''
        localStorage.removeItem('admin_token')
      }
      return null
    } finally {
      loading.value = false
    }
  }

  function clearAuth() {
    token.value = ''
    adminInfo.value = null
    localStorage.removeItem('admin_token')
    logger.info('[AdminStore] Auth cleared')
  }

  return {
    token,
    adminInfo,
    loading,
    isLoggedIn,
    isSuperAdmin,
    isAuditor,
    login,
    logout,
    fetchProfile,
    clearAuth
  }
})