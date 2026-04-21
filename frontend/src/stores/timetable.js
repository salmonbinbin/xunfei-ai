import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getTodayCourses, getCourses, getWeekTimetable, getCourseDetail, generateAIInsights, aiChatAboutCourse } from '@/api/timetable'
import { getSchedules } from '@/api/schedule'

export const useTimetableStore = defineStore('timetable', () => {
  const courses = ref([])
  const schedules = ref([])
  const currentWeek = ref(1)
  const loading = ref(false)
  const weekCourses = ref({})
  const className = ref(null)  // 用户班别

  const todayCourses = computed(() => {
    const today = new Date().getDay()
    const dayMap = { 0: 7, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6 }
    const dayOfWeek = dayMap[today]
    return courses.value
      .filter(c => c.day_of_week === dayOfWeek)
      .map(c => ({
        ...c,
        // 清理课程名中的节次信息
        name: c.name.replace(/\s*[\(（【\[【]?\d+[\-－]\d+\s*节?\s*[\)）】\]】]?\s*$/g, '').trim()
      }))
      .sort((a, b) => a.start_slot - b.start_slot)
  })

  /**
   * 获取今日课程和日程
   */
  async function fetchTodayData() {
    loading.value = true
    try {
      const res = await getTodayCourses()
      courses.value = res.data?.courses || []
      schedules.value = res.data?.schedules || []
      className.value = res.data?.class_name || null
    } catch (error) {
      console.error('[Store] Failed to fetch today data:', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取课程列表
   * @param {number} dayOfWeek - 星期几
   */
  async function fetchCourses(dayOfWeek) {
    loading.value = true
    try {
      const res = await getCourses(dayOfWeek)
      courses.value = res.data || []
    } catch (error) {
      console.error('[Store] Failed to fetch courses:', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取周课表
   * @param {number} weekOffset - 周偏移量
   */
  async function fetchWeekTimetable(weekOffset = 0) {
    loading.value = true
    try {
      const res = await getWeekTimetable(weekOffset)
      weekCourses.value = res.data?.courses || {}
      return res.data
    } catch (error) {
      console.error('[Store] Failed to fetch week timetable:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取课程详情（含AI洞察）
   * @param {number} courseId - 课程ID
   */
  async function fetchCourseDetail(courseId) {
    try {
      const res = await getCourseDetail(courseId)
      return res.data
    } catch (error) {
      console.error('[Store] Failed to fetch course detail:', error)
      return null
    }
  }

  /**
   * 生成AI学习建议
   * @param {number} courseId - 课程ID
   */
  async function generateInsights(courseId) {
    loading.value = true
    try {
      const res = await generateAIInsights(courseId)
      return res.data
    } catch (error) {
      console.error('[Store] Failed to generate AI insights:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * AI学伴问答
   * @param {number} courseId - 课程ID
   * @param {string} question - 问题
   */
  async function chatWithAI(courseId, question) {
    loading.value = true
    try {
      const res = await aiChatAboutCourse(courseId, question)
      return res.data?.answer
    } catch (error) {
      console.error('[Store] Failed to chat with AI:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  function setCourses(newCourses) {
    courses.value = newCourses
  }

  function addCourse(course) {
    courses.value.push(course)
  }

  function removeCourse(courseId) {
    courses.value = courses.value.filter(c => c.id !== courseId)
  }

  function setCurrentWeek(week) {
    currentWeek.value = week
  }

  return {
    courses,
    schedules,
    currentWeek,
    loading,
    weekCourses,
    className,
    todayCourses,
    fetchTodayData,
    fetchCourses,
    fetchWeekTimetable,
    fetchCourseDetail,
    generateInsights,
    chatWithAI,
    setCourses,
    addCourse,
    removeCourse,
    setCurrentWeek
  }
})
