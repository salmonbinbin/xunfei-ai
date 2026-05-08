<template>
  <div class="grade-detail-page">
    <!-- 顶部导航 -->
    <div class="detail-nav">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <div class="nav-title">
        <h2>{{ courseName }}</h2>
        <span class="nav-sub" v-if="record?.semester">{{ record.semester }}</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" class="loading-container">
      <!-- 统计数据卡片 -->
      <div class="stats-cards">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon primary">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ basicStats?.avg_score || '-' }}</span>
              <span class="stat-label">平均分</span>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ basicStats ? (basicStats.pass_rate * 100).toFixed(1) + '%' : '-' }}</span>
              <span class="stat-label">及格率</span>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon warning">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ basicStats?.max_score || '-' }}</span>
              <span class="stat-label">最高分</span>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon danger">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ basicStats?.min_score != null ? basicStats.min_score : '-' }}</span>
              <span class="stat-label">最低分</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <!-- 成绩分布直方图 -->
        <el-card class="chart-card">
          <div ref="distributionChartRef" class="chart-container"></div>
        </el-card>

        <!-- 雷达图 -->
        <el-card class="chart-card" v-if="showRadar">
          <template #header>
            <div class="radar-header">
              <span>学生能力雷达图</span>
              <div class="student-search">
                <el-input
                  v-model="searchStudentName"
                  placeholder="输入学生姓名搜索"
                  size="small"
                  clearable
                  @keyup.enter="searchStudent"
                >
                  <template #append>
                    <el-button @click="searchStudent" :icon="Search" />
                  </template>
                </el-input>
              </div>
            </div>
          </template>
          <div ref="radarChartRef" class="chart-container"></div>
          <!-- 搜索学生单独显示 -->
          <div v-if="searchedStudent" class="searched-student-radar">
            <div class="searched-title">{{ searchedStudent.student_name }} 的能力分析</div>
            <div ref="searchedStudentChartRef" class="chart-container-small"></div>
          </div>
        </el-card>
      </div>

      <!-- AI分析报告 -->
      <el-card class="report-card">
        <template #header>
          <div class="report-header">
            <span class="report-title">AI分析报告</span>
            <el-button text type="primary" @click="refreshReport" :loading="reportLoading">
              <el-icon><Refresh /></el-icon>
              重新生成
            </el-button>
          </div>
        </template>
        <div v-if="report" class="report-content">
          <p class="report-summary">{{ report.summary }}</p>

          <div class="report-section">
            <h4>📌 试卷分析</h4>
            <div class="exam-analysis">
              <span class="analysis-item">
                难度系数：{{ report.exam_analysis.difficulty }}（{{ report.exam_analysis.difficulty_text }}）
              </span>
              <span class="analysis-item">
                区分度：{{ report.exam_analysis.discrimination }}（{{ report.exam_analysis.discrimination_text }}）
              </span>
            </div>
          </div>

          <div class="report-section" v-if="report.high_performers?.length">
            <h4>🌟 高分学生</h4>
            <div class="student-tags">
              <el-tag v-for="name in report.high_performers" :key="name" type="success" effect="light">
                {{ name }}
              </el-tag>
            </div>
          </div>

          <div class="report-section" v-if="report.needs_attention?.length">
            <h4>⚠️ 需要关注</h4>
            <div class="student-tags">
              <el-tag v-for="name in report.needs_attention" :key="name" type="warning" effect="light">
                {{ name }}
              </el-tag>
            </div>
          </div>

          <div class="report-section" v-if="report.suggestions">
            <h4>💡 教学建议</h4>
            <p class="suggestions">{{ report.suggestions }}</p>
          </div>
        </div>
        <div v-else-if="reportLoading" class="report-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在生成AI分析报告...</span>
        </div>
        <div v-else class="report-empty">
          <p>暂无分析报告</p>
          <el-button type="primary" @click="refreshReport">生成报告</el-button>
        </div>
      </el-card>

      <!-- 成绩明细表格 -->
      <el-card class="table-card">
        <template #header>
          <div class="table-header">
            <span>成绩明细</span>
            <el-button type="primary" size="small" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出成绩单
            </el-button>
          </div>
        </template>

        <el-table
          ref="tableRef"
          :data="items"
          stripe
          border
          style="width: 100%"
          :default-sort="{ prop: 'rank', order: 'ascending' }"
          @sort-change="handleSortChange"
        >
          <el-table-column prop="rank" label="排名" width="80" sortable />
          <el-table-column prop="student_name" label="学生姓名" min-width="100" />
          <el-table-column prop="student_no" label="学号" width="120" />
          <el-table-column prop="usual_score" label="平时分" width="90" sortable />
          <el-table-column prop="midterm_score" label="期中分" width="90" sortable />
          <el-table-column prop="final_score" label="期末分" width="90" sortable />
          <el-table-column prop="practice_score" label="实验分" width="90" sortable />
          <el-table-column prop="total_score" label="总评" width="90" sortable>
            <template #default="{ row }">
              <span :class="getScoreClass(row.total_score)">{{ row.total_score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.status !== 'normal'" :type="row.status === 'absent' ? 'danger' : 'warning'" size="small">
                {{ row.status === 'absent' ? '缺考' : '缓考' }}
              </el-tag>
              <span v-else class="status-normal">正常</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Download, Loading, Search } from '@element-plus/icons-vue'
import { useGradeStore } from '@/stores/grade'
import { exportGradeExcel } from '@/api/grade'
import {
  getDistributionChart,
  getRadarChart,
  createChart,
  disposeChart
} from '@/utils/gradeChart'

const route = useRoute()
const router = useRouter()
const gradeStore = useGradeStore()

// 状态
const loading = ref(false)
const reportLoading = ref(false)
const record = ref(null)
const items = ref([])
const report = ref(null)
const basicStats = ref(null)
const distribution = ref([])
const searchStudentName = ref('')
const searchedStudent = ref(null)

// 图表ref
const distributionChartRef = ref(null)
const radarChartRef = ref(null)
const searchedStudentChartRef = ref(null)
const charts = ref([])

// 表格ref和排序状态
const tableRef = ref(null)
const tableSort = ref({ prop: 'rank', order: 'ascending' })

// 排序变化处理
function handleSortChange({ prop, order }) {
  tableSort.value = { prop: prop || 'rank', order: order || 'ascending' }
}

// 计算属性
const courseName = computed(() => record.value?.course_name || '成绩详情')
const showRadar = computed(() => items.value.length > 0 && items.value.length <= 50)

function goBack() {
  router.push('/teacher/grade')
}

async function fetchDetail() {
  loading.value = true
  try {
    const recordId = route.params.id
    const res = await gradeStore.fetchDetail(recordId)
    if (res) {
      record.value = res
      items.value = res.items || []
      basicStats.value = res.stats?.basic
      distribution.value = res.stats?.distribution || []

      // 渲染图表
      await nextTick()
      renderCharts()
    }
  } catch (error) {
    console.error('Fetch detail error:', error)
    ElMessage.error('获取成绩详情失败')
  } finally {
    loading.value = false
  }
}

async function refreshReport() {
  reportLoading.value = true
  try {
    const recordId = route.params.id
    const res = await gradeStore.fetchReport(recordId, true)
    if (res) {
      report.value = res
      ElMessage.success('报告已更新')
    }
  } catch (error) {
    console.error('Fetch report error:', error)
    ElMessage.error('生成报告失败')
  } finally {
    reportLoading.value = false
  }
}

async function handleExport() {
  try {
    const recordId = route.params.id
    const token = localStorage.getItem('token')

    // 构建带排序参数的URL
    const sortBy = tableSort.value.prop === 'rank' ? 'rank' : tableSort.value.prop
    const sortOrder = tableSort.value.order === 'ascending' ? 'ascending' : 'descending'
    const exportUrl = `/api/teacher/grade/records/${recordId}/export?sort_by=${sortBy}&sort_order=${sortOrder}`

    // 直接使用fetch下载，避免axios处理blob的问题
    const response = await fetch(exportUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.error?.message) {
        ElMessage.error(errorData.error.message)
      } else if (errorData.detail) {
        ElMessage.error(errorData.detail)
      } else {
        ElMessage.error(`导出失败：${response.status}`)
      }
      return
    }

    const blob = await response.blob()

    if (blob.size > 0) {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${courseName.value}_成绩单.xlsx`
      link.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败：文件为空')
    }
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败，请检查网络')
  }
}

function getScoreClass(score) {
  if (!score) return ''
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

function searchStudent() {
  if (!searchStudentName.value.trim()) {
    searchedStudent.value = null
    return
  }
  const found = items.value.find(
    item => item.student_name.includes(searchStudentName.value.trim())
  )
  if (found) {
    searchedStudent.value = found
    nextTick(() => {
      renderSearchedStudentChart()
    })
  } else {
    ElMessage.warning('未找到该学生')
    searchedStudent.value = null
  }
}

function renderSearchedStudentChart() {
  if (searchedStudentChartRef.value && searchedStudent.value) {
    const chart = createChart(searchedStudentChartRef.value, getRadarChart([searchedStudent.value], 1))
    charts.value.push(chart)
  }
}

function renderCharts() {
  // 清理旧图表
  charts.value.forEach(disposeChart)
  charts.value = []

  // 成绩分布图
  if (distributionChartRef.value && distribution.value.length > 0) {
    const distChart = createChart(distributionChartRef.value, getDistributionChart(distribution.value))
    charts.value.push(distChart)
  }

  // 雷达图
  if (radarChartRef.value && showRadar.value) {
    const radarChart = createChart(radarChartRef.value, getRadarChart(items.value))
    charts.value.push(radarChart)
  }

  // 搜索学生雷达图
  if (searchedStudent.value && searchedStudentChartRef.value) {
    renderSearchedStudentChart()
  }
}

function handleResize() {
  charts.value.forEach(chart => chart?.resize())
}

onMounted(() => {
  fetchDetail()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.value.forEach(disposeChart)
})
</script>

<style scoped>
.grade-detail-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.nav-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.nav-title h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.nav-sub {
  color: #94A3B8;
  font-size: 14px;
}

.loading-container {
  min-height: 400px;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  border-radius: 12px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.primary {
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.1), rgba(34, 211, 238, 0.05));
  color: #0891B2;
}

.stat-icon.success {
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(52, 211, 153, 0.05));
  color: #059669;
}

.stat-icon.warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.05));
  color: #F59E0B;
}

.stat-icon.danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(248, 113, 113, 0.05));
  color: #EF4444;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #94A3B8;
  margin-top: 2px;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.radar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.student-search {
  width: 200px;
}

.searched-student-radar {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #F1F5F9;
}

.searched-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.chart-container-small {
  width: 100%;
  height: 350px;
}

/* AI报告卡片 */
.report-card {
  border-radius: 12px;
  margin-bottom: 24px;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.report-content {
  padding: 8px 0;
}

.report-summary {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
  margin: 0 0 20px;
  padding: 12px 16px;
  background: #F8FAFC;
  border-radius: 8px;
  border-left: 3px solid #0891B2;
}

.report-section {
  margin-bottom: 16px;
}

.report-section h4 {
  font-size: 14px;
  color: #1E293B;
  margin: 0 0 8px;
}

.exam-analysis {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.analysis-item {
  font-size: 14px;
  color: #64748B;
}

.student-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestions {
  font-size: 14px;
  color: #64748B;
  line-height: 1.6;
  margin: 0;
}

.report-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #94A3B8;
}

.report-empty {
  text-align: center;
  padding: 40px;
  color: #94A3B8;
}

/* 表格卡片 */
.table-card {
  border-radius: 12px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #1E293B;
}

/* 分数样式 */
.score-excellent {
  color: #059669;
  font-weight: 600;
}

.score-good {
  color: #0891B2;
  font-weight: 600;
}

.score-average {
  color: #F59E0B;
}

.score-pass {
  color: #64748B;
}

.score-fail {
  color: #EF4444;
  font-weight: 600;
}

.status-normal {
  color: #94A3B8;
  font-size: 13px;
}
</style>
