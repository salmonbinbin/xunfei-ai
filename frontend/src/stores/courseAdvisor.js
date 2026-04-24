import { defineStore } from 'pinia'
import api from '@/api/index'
import { getStudentProfile, getRecommendations, getCourseDetail, chatConsultation, confirmSelection, getMySelectedCourses, searchCourseByName } from '@/api/courseAdvisor'

// 计算动态雷达数据
function calculateDynamicRadarData(courses, goal) {
  if (!courses || courses.length === 0) {
    return { '专业知识覆盖度': 0, '目标匹配度': 0 }
  }

  // 专业知识覆盖度：根据已选课程数量计算
  // 每门课程约覆盖5-10%的知识领域
  const courseCount = courses.length
  const majorCoverage = Math.min(100, courseCount * 8 + 10)

  // 目标匹配度：根据课程与目标的匹配度计算
  const goalKeywords = {
    '考研': ['数据结构', '算法', '高等数学', '线性代数', '概率论', '计算机网络', '操作系统'],
    '考公': ['法律', '政治', '行政', '申论'],
    '就业': ['软件工程', '数据库', '前端', '后端', '框架', '实践', '项目'],
    '出国': ['英语', '口语', '写作', '雅思', '托福']
  }

  let goalMatch = 30 // 默认30%
  if (goal && goalKeywords[goal]) {
    const keywords = goalKeywords[goal]
    const matchedCourses = courses.filter(c =>
      keywords.some(kw => c.name && c.name.includes(kw))
    )
    if (matchedCourses.length > 0) {
      goalMatch = Math.min(100, 30 + matchedCourses.length * 15)
    }
  }

  return {
    '专业知识覆盖度': majorCoverage,
    '目标匹配度': goalMatch
  }
}

export const useCourseAdvisorStore = defineStore('courseAdvisor', {
  state: () => ({
    // 学生画像
    profile: {
      major: '',
      grade: 0,
      goal: '',
      gpa: 0,
      completed_credits: 0,
      required_credits: 160,
      radar_data: {
        '专业知识覆盖度': 0,
        '目标匹配度': 0
      },
      ability_type: '逻辑型',
      ai_suggestion: ''
    },

    // 推荐课程
    recommendedCourses: [],
    totalCredits: 0,

    // 已选课程列表（用于计算雷达图）
    mySelectedCourses: [],

    // 分页信息
    pagination: {
      page: 1,
      pageSize: 3,
      total: 0,
      totalPages: 0
    },

    // 当前选中的类别
    currentCategory: 'all',

    // 当前学期
    currentSemester: '2024-1',

    // 加载状态
    loading: {
      profile: false,
      recommendations: false,
      chat: false
    },

    // 错误信息
    error: null,

    // 对话历史
    chatHistory: [],

    // AI回复
    aiReply: '',
    suggestedCourses: [],

    // 选课方案
    selectedCourseIds: [],
    planId: null,
    conflicts: []
  }),

  getters: {
    // 雷达图数据
    radarData: (state) => {
      // 如果有已选课程，基于已选课程计算动态雷达数据
      if (state.mySelectedCourses.length > 0) {
        return calculateDynamicRadarData(state.mySelectedCourses, state.profile.goal)
      }
      return state.profile.radar_data
    },

    // 学分进度
    creditProgress: (state) => {
      return {
        completed: state.profile.completed_credits,
        required: state.profile.required_credits,
        percentage: Math.round((state.profile.completed_credits / state.profile.required_credits) * 100)
      }
    },

    // 是否正在加载
    isLoading: (state) => state.loading.profile || state.loading.recommendations || state.loading.chat
  },

  actions: {
    // 获取学生画像
    async fetchProfile() {
      this.loading.profile = true
      this.error = null

      try {
        const response = await getStudentProfile()
        if (response.data.success) {
          this.profile = {
            major: response.data.major,
            grade: response.data.grade,
            goal: response.data.goal,
            gpa: response.data.gpa,
            completed_credits: response.data.completed_credits,
            required_credits: response.data.required_credits,
            radar_data: response.data.radar_data,
            ability_type: response.data.ability_type,
            ai_suggestion: response.data.ai_suggestion
          }
        }
      } catch (error) {
        this.error = error.message || '获取学生画像失败'
        console.error('[CourseAdvisor] Failed to fetch profile:', error)
      } finally {
        this.loading.profile = false
      }
    },

    // 获取推荐课程
    async fetchRecommendations(category = 'all', goalFilter = null, page = 1) {
      this.loading.recommendations = true
      this.error = null
      this.currentCategory = category

      try {
        const response = await getRecommendations({
          semester: this.currentSemester,
          category,
          goal_filter: goalFilter,
          page,
          page_size: this.pagination.pageSize
        })

        if (response.data.success) {
          this.recommendedCourses = response.data.courses.map(course => ({
            ...course,
            conflict_status: course.conflict_status || 'none'
          }))
          this.totalCredits = response.data.total_credits
          this.pagination = {
            page: response.data.page,
            pageSize: response.data.page_size,
            total: response.data.total,
            totalPages: response.data.total_pages
          }
        }
      } catch (error) {
        this.error = error.message || '获取推荐失败'
        console.error('[CourseAdvisor] Failed to fetch recommendations:', error)
      } finally {
        this.loading.recommendations = false
      }
    },

    // 获取课程详情
    async fetchCourseDetail(courseId) {
      try {
        const response = await getCourseDetail(courseId)
        if (response.data.success) {
          return response.data
        }
        return null
      } catch (error) {
        console.error('[CourseAdvisor] Failed to fetch course detail:', error)
        return null
      }
    },

    // 对话咨询
    async sendChat(message) {
      this.loading.chat = true

      // 添加用户消息到历史
      this.chatHistory.push({
        role: 'user',
        content: message,
        timestamp: Date.now()
      })

      try {
        const response = await chatConsultation({
          message,
          history: this.chatHistory.slice(-10)
        })

        if (response.data.success) {
          this.aiReply = response.data.reply
          this.suggestedCourses = response.data.recommended_courses || []

          // 添加AI回复到历史
          this.chatHistory.push({
            role: 'assistant',
            content: response.data.reply,
            timestamp: Date.now()
          })

          return response.data
        }
      } catch (error) {
        console.error('[CourseAdvisor] Failed to send chat:', error)
        this.aiReply = '抱歉，我现在无法回答您的问题，请稍后再试。'
      } finally {
        this.loading.chat = false
      }
    },

    // 选择/取消选择课程
    toggleCourseSelection(courseId) {
      const index = this.selectedCourseIds.indexOf(courseId)
      if (index > -1) {
        this.selectedCourseIds.splice(index, 1)
      } else {
        this.selectedCourseIds.push(courseId)
      }
    },

    // 确认选课方案
    async submitSelection() {
      if (this.selectedCourseIds.length === 0) {
        this.error = '请至少选择一门课程'
        return null
      }

      try {
        const response = await confirmSelection({
          semester: this.currentSemester,
          selected_courses: this.selectedCourseIds
        })

        if (response.data.success) {
          this.planId = response.data.plan_id
          this.conflicts = response.data.conflicts || []

          // 将选中的课程添加到已选列表
          const selectedCourses = this.recommendedCourses.filter(c =>
            this.selectedCourseIds.includes(c.id)
          )
          this.mySelectedCourses = [...this.mySelectedCourses, ...selectedCourses]

          // 清空已选ID
          this.selectedCourseIds = []

          return response.data
        }
      } catch (error) {
        this.error = error.message || '保存选课方案失败'
        console.error('[CourseAdvisor] Failed to confirm selection:', error)
      }

      return null
    },

    // 清除对话历史
    clearChatHistory() {
      this.chatHistory = []
      this.aiReply = ''
      this.suggestedCourses = []
    },

    // 设置当前学期
    setSemester(semester) {
      this.currentSemester = semester
    },

    // 检测时间冲突
    detectConflicts() {
      const selectedCourses = this.recommendedCourses.filter(c =>
        this.selectedCourseIds.includes(c.id)
      )

      const conflicts = []
      const slotMap = new Map()

      for (const course of selectedCourses) {
        const key = `${course.day_of_week}-${course.start_slot}`
        if (slotMap.has(key)) {
          conflicts.push({
            course1: slotMap.get(key),
            course2: course
          })
        } else {
          slotMap.set(key, course)
        }
      }

      return conflicts
    },

    // 获取我的已选课程
    async fetchMySelectedCourses() {
      this.loading.recommendations = true
      this.error = null

      try {
        const response = await getMySelectedCourses(this.currentSemester)
        if (response.data.success) {
          this.recommendedCourses = response.data.courses.map(course => ({
            ...course,
            conflict_status: course.conflict_status || 'none'
          }))
          this.totalCredits = response.data.total_credits || 0
          this.pagination = {
            page: 1,
            pageSize: this.pagination.pageSize, // 保持每页3门课程
            total: response.data.courses.length,
            totalPages: Math.ceil(response.data.courses.length / this.pagination.pageSize) || 1
          }
          // 更新已选课程列表（用于雷达图计算）
          this.mySelectedCourses = [...response.data.courses]
        }
      } catch (error) {
        this.error = error.message || '获取已选课程失败'
        console.error('[CourseAdvisor] Failed to fetch my selected courses:', error)
      } finally {
        this.loading.recommendations = false
      }
    },

    // 根据课程名称搜索课程目录
    async searchCourseByName(name) {
      try {
        return await searchCourseByName(name)
      } catch (error) {
        console.error('[CourseAdvisor] Failed to search course:', error)
        return null
      }
    }
  }
})