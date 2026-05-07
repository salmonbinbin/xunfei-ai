<template>
  <div class="teacher-grade-page">
    <div class="page-header">
      <h1>智能成绩管理</h1>
      <el-tag type="info" effect="plain">AI智能分析</el-tag>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section" v-if="!uploading">
      <el-card class="upload-card">
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
        >
          <div class="upload-content">
            <div class="upload-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 17v-2m3 2v-4m3 4v-6m5 4H5a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div class="upload-text">
              <span class="primary-text">点击或拖拽上传成绩表</span>
              <span class="sub-text">支持 .xlsx 和 .xls 格式，最大 5MB</span>
            </div>
          </div>
        </el-upload>
      </el-card>
    </div>

    <!-- 上传进度 -->
    <div class="uploading-section" v-else>
      <el-card class="uploading-card">
        <div class="uploading-content">
          <el-progress :percentage="uploadProgress" type="circle" :width="100" />
          <p class="uploading-text">正在解析成绩数据...</p>
        </div>
      </el-card>
    </div>

    <!-- 上传配置弹窗 -->
    <el-dialog
      v-model="showConfigDialog"
      title="配置成绩信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="uploadConfig" label-width="80px">
        <el-form-item label="课程名称" required>
          <el-input v-model="uploadConfig.courseName" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="班级名称">
          <el-input v-model="uploadConfig.className" placeholder="请输入班级名称（选填）" />
        </el-form-item>
        <el-form-item label="学期">
          <el-input v-model="uploadConfig.semester" placeholder="如：2026春季" />
        </el-form-item>
        <el-form-item label="成绩权重">
          <div class="weight-config">
            <el-slider
              v-model="uploadConfig.weights.usual"
              :min="0"
              :max="1"
              :step="0.05"
              show-input
              :format-tooltip="v => (v * 100).toFixed(0) + '%'"
            />
            <span class="weight-label">平时分 {{ (uploadConfig.weights.usual * 100).toFixed(0) }}%</span>
          </div>
          <div class="weight-config">
            <el-slider
              v-model="uploadConfig.weights.midterm"
              :min="0"
              :max="1"
              :step="0.05"
              show-input
              :format-tooltip="v => (v * 100).toFixed(0) + '%'"
            />
            <span class="weight-label">期中分 {{ (uploadConfig.weights.midterm * 100).toFixed(0) }}%</span>
          </div>
          <div class="weight-config">
            <el-slider
              v-model="uploadConfig.weights.final"
              :min="0"
              :max="1"
              :step="0.05"
              show-input
              :format-tooltip="v => (v * 100).toFixed(0) + '%'"
            />
            <span class="weight-label">期末分 {{ (uploadConfig.weights.final * 100).toFixed(0) }}%</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelUpload">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :loading="uploading">
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览结果弹窗 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="成绩上传成功"
      width="600px"
    >
      <div class="preview-content" v-if="uploadResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程名称">{{ uploadResult.course_name }}</el-descriptions-item>
          <el-descriptions-item label="学生人数">{{ uploadResult.item_count }}人</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ uploadResult.stats.avg_score }}</el-descriptions-item>
          <el-descriptions-item label="及格率">{{ (uploadResult.stats.pass_rate * 100).toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="goToRecords">查看成绩</el-button>
        <el-button type="primary" @click="showPreviewDialog = false">完成</el-button>
      </template>
    </el-dialog>

    <!-- 历史记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h2>历史成绩</h2>
        <span class="record-count">共 {{ total }} 条记录</span>
      </div>

      <div v-loading="loading" class="records-list">
        <!-- 空状态 -->
        <el-empty v-if="!loading && records.length === 0" description="暂无成绩记录">
          <el-button type="primary" @click="focusUpload">上传第一个成绩</el-button>
        </el-empty>

        <!-- 记录卡片 -->
        <div v-else class="record-cards">
          <el-card
            v-for="record in records"
            :key="record.id"
            class="record-card"
            shadow="hover"
            @click="goToDetail(record.id)"
          >
            <div class="record-main">
              <div class="record-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
              </div>
              <div class="record-info">
                <h3 class="record-title">{{ record.course_name }}</h3>
                <p class="record-meta">
                  <span v-if="record.class_name">{{ record.class_name }}</span>
                  <span v-if="record.semester">{{ record.semester }}</span>
                  <span>{{ record.student_count }}人</span>
                </p>
              </div>
            </div>
            <div class="record-stats">
              <div class="stat-item">
                <span class="stat-value">{{ record.avg_score || '-' }}</span>
                <span class="stat-label">平均分</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ record.pass_rate ? (record.pass_rate * 100).toFixed(0) + '%' : '-' }}</span>
                <span class="stat-label">及格率</span>
              </div>
            </div>
            <div class="record-footer">
              <span class="record-date">{{ formatDate(record.created_at) }}</span>
              <el-button text type="danger" size="small" @click.stop="handleDelete(record.id)">
                删除
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useGradeStore } from '@/stores/grade'
import { uploadGrade, exportGradeExcel } from '@/api/grade'

const router = useRouter()
const gradeStore = useGradeStore()

// 状态
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// 上传相关
const uploadRef = ref(null)
const selectedFile = ref(null)
const showConfigDialog = ref(false)
const showPreviewDialog = ref(false)
const uploadResult = ref(null)

const uploadConfig = reactive({
  courseName: '',
  className: '',
  semester: '',
  weights: {
    usual: 0.4,
    midterm: 0.2,
    final: 0.4,
    practice: 0
  }
})

// 文件选择
function handleFileChange(file) {
  selectedFile.value = file.raw
  uploadConfig.courseName = ''

  // 尝试从文件名提取课程名
  const filename = file.name.replace(/\.(xlsx|xls)$/i, '')
  if (filename) {
    uploadConfig.courseName = filename
  }

  showConfigDialog.value = true
}

function handleFileRemove() {
  selectedFile.value = null
}

function cancelUpload() {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
  showConfigDialog.value = false
}

async function confirmUpload() {
  if (!uploadConfig.courseName) {
    ElMessage.warning('请输入课程名称')
    return
  }

  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 10
  showConfigDialog.value = false

  try {
    const formData = new FormData()
    console.log('selectedFile:', selectedFile.value)
    console.log('selectedFile type:', typeof selectedFile.value)
    console.log('selectedFile name:', selectedFile.value?.name)
    console.log('selectedFile size:', selectedFile.value?.size)
    formData.append('file', selectedFile.value)
    formData.append('course_name', uploadConfig.courseName)
    if (uploadConfig.className) {
      formData.append('class_name', uploadConfig.className)
    }
    if (uploadConfig.semester) {
      formData.append('semester', uploadConfig.semester)
    }
    formData.append('weights_json', JSON.stringify(uploadConfig.weights))

    // Debug: check FormData contents
    console.log('FormData file:', formData.get('file'))

    uploadProgress.value = 50

    const res = await uploadGrade(formData)

    uploadProgress.value = 100

    if (res.data.success) {
      uploadResult.value = res.data.data
      showPreviewDialog.value = true
      ElMessage.success('成绩上传成功')
      await fetchRecords()
    } else {
      ElMessage.error(res.data.error?.message || '上传失败')
    }
  } catch (error) {
    console.error('Upload error:', error)
    const errorData = error?.response?.data
    console.error('Error data:', JSON.stringify(errorData, null, 2))
    if (errorData?.error?.message) {
      ElMessage.error(errorData.error.message)
    } else if (errorData?.detail) {
      ElMessage.error(errorData.detail)
    } else {
      ElMessage.error('上传失败，请重试')
    }
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    selectedFile.value = null
    uploadRef.value?.clearFiles()
  }
}

function goToRecords() {
  showPreviewDialog.value = false
  page.value = 1
  fetchRecords()
}

function goToDetail(recordId) {
  router.push(`/teacher/grade/${recordId}`)
}

async function handleDelete(recordId) {
  try {
    await ElMessageBox.confirm('确定要删除这条成绩记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await gradeStore.deleteRecord(recordId)
    ElMessage.success('删除成功')
    await fetchRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchRecords()
}

function focusUpload() {
  document.querySelector('.upload-section')?.scrollIntoView({ behavior: 'smooth' })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

async function fetchRecords() {
  loading.value = true
  try {
    const res = await gradeStore.fetchRecords({ page: page.value, page_size: pageSize.value })
    if (res) {
      records.value = res.records || []
      total.value = res.total || 0
    }
  } catch (error) {
    console.error('Fetch records error:', error)
    ElMessage.error('获取成绩记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.teacher-grade-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 32px;
}

.upload-card {
  border-radius: 16px;
  overflow: hidden;
}

.upload-card :deep(.el-card__body) {
  padding: 0;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  min-height: 200px;
}

.upload-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08), rgba(34, 211, 238, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
}

.primary-text {
  display: block;
  font-size: 16px;
  color: #1E293B;
  font-weight: 500;
  margin-bottom: 4px;
}

.sub-text {
  display: block;
  font-size: 14px;
  color: #94A3B8;
}

/* 上传进度 */
.uploading-section {
  margin-bottom: 32px;
}

.uploading-card {
  border-radius: 16px;
}

.uploading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
}

.uploading-text {
  margin-top: 16px;
  color: #64748B;
}

/* 配置弹窗 */
.weight-config {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.weight-config:last-child {
  margin-bottom: 0;
}

.weight-label {
  min-width: 100px;
  color: #64748B;
  font-size: 14px;
}

/* 预览内容 */
.preview-content {
  padding: 16px 0;
}

/* 历史记录 */
.records-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.record-count {
  color: #94A3B8;
  font-size: 14px;
}

.records-list {
  min-height: 200px;
}

.record-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.record-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.record-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  border-color: #CBD5E1;
}

.record-main {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.record-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08), rgba(34, 211, 238, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
  flex-shrink: 0;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-meta {
  font-size: 13px;
  color: #94A3B8;
  margin: 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.record-meta span:not(:last-child)::after {
  content: '·';
  margin-left: 8px;
}

.record-stats {
  display: flex;
  gap: 24px;
  padding: 12px 0;
  border-top: 1px solid #F1F5F9;
  border-bottom: 1px solid #F1F5F9;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #0891B2;
}

.stat-label {
  font-size: 12px;
  color: #94A3B8;
}

.record-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.record-date {
  font-size: 12px;
  color: #CBD5E1;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
