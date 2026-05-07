import { defineStore } from 'pinia'
import {
  getGradeRecords,
  getGradeDetail,
  getGradeReport,
  deleteGradeRecord
} from '@/api/grade'

export const useGradeStore = defineStore('grade', {
  state: () => ({
    records: [],
    currentRecord: null,
    currentStats: null,
    currentReport: null,
    loading: false,
    total: 0,
    page: 1,
    pageSize: 10
  }),

  getters: {
    hasRecords: (state) => state.records.length > 0
  },

  actions: {
    async fetchRecords(params = {}) {
      this.loading = true
      try {
        const res = await getGradeRecords({
          page: this.page,
          page_size: this.pageSize,
          ...params
        })
        // res.data is the API response body: {success: true, data: {records, total, ...}}
        const data = res.data?.data
        if (data) {
          this.records = data.records || []
          this.total = data.total || 0
          this.page = data.page || 1
          this.pageSize = data.page_size || 10
        }
        return data
      } finally {
        this.loading = false
      }
    },

    async fetchDetail(recordId) {
      this.loading = true
      try {
        const res = await getGradeDetail(recordId)
        const data = res.data?.data
        if (data) {
          this.currentRecord = data
          this.currentStats = data.stats
        }
        return data
      } finally {
        this.loading = false
      }
    },

    async fetchReport(recordId, regenerate = false) {
      this.loading = true
      try {
        const res = await getGradeReport(recordId, regenerate)
        const data = res.data?.data
        if (data) {
          this.currentReport = data
        }
        return data
      } finally {
        this.loading = false
      }
    },

    async deleteRecord(recordId) {
      this.loading = true
      try {
        await deleteGradeRecord(recordId)
        // 从列表中移除
        this.records = this.records.filter(r => r.id !== recordId)
        this.total = Math.max(0, this.total - 1)
      } catch (e) {
        console.error('[GradeStore] deleteRecord error:', e)
        throw e
      } finally {
        this.loading = false
      }
    },

    setPage(page) {
      this.page = page
    },

    clearCurrentRecord() {
      this.currentRecord = null
      this.currentStats = null
      this.currentReport = null
    }
  }
})
