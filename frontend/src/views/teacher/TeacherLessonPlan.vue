<template>
  <div class="lesson-plan-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <h1 class="page-title">智能备课教案</h1>
      <p class="page-subtitle">输入知识点，AI一键生成教学大纲和PPT</p>
    </div>

    <div class="page-content">
      <!-- 左侧：创建教案表单 -->
      <div class="left-panel">
        <!-- 创建教案卡片 -->
        <div class="card">
          <h3 class="card-title">创建教案</h3>
          <el-form :model="form" label-position="top" :rules="formRules" ref="formRef">
            <el-form-item label="教案标题" prop="title">
              <el-input
                v-model="form.title"
                placeholder="例如：计算机网络TCP/IP协议"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="课程名称" prop="courseName">
              <el-input
                v-model="form.courseName"
                placeholder="例如：计算机网络基础"
                maxlength="100"
              />
            </el-form-item>

            <el-form-item label="知识点描述" prop="knowledgePoints">
              <el-input
                v-model="form.knowledgePoints"
                type="textarea"
                :rows="4"
                placeholder="请详细描述需要涵盖的知识点，例如：&#10;1. TCP/IP四层模型&#10;2. IP地址分类与子网掩码&#10;3. TCP三次握手四次挥手&#10;4. UDP与TCP区别"
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="授课对象" prop="targetAudience">
              <el-input
                v-model="form.targetAudience"
                placeholder="例如：计算机科学与技术专业大二学生"
                maxlength="100"
              />
            </el-form-item>

            <el-form-item label="课时数" prop="teachingHours">
              <el-input-number
                v-model="form.teachingHours"
                :min="1"
                :max="100"
                placeholder="预计课时数"
              />
            </el-form-item>

            <div class="form-actions">
              <el-button @click="resetForm">重置</el-button>
              <el-button type="primary" :loading="generatingOutline" @click="handleGenerateOutline">
                生成大纲
              </el-button>
              <el-button type="success" :loading="generatingPpt" @click="handleGeneratePpt" :disabled="!outlineReady">
                生成PPT
              </el-button>
            </div>
          </el-form>
        </div>

        <!-- PPT模板选择卡片 -->
        <div class="card">
          <h3 class="card-title">PPT模板</h3>

          <!-- 筛选器 -->
          <div class="filter-row">
            <el-select v-model="filters.style" placeholder="风格" clearable @change="loadThemes">
              <el-option label="简约" value="简约" />
              <el-option label="卡通" value="卡通" />
              <el-option label="商务" value="商务" />
              <el-option label="创意" value="创意" />
              <el-option label="国风" value="国风" />
              <el-option label="清新" value="清新" />
              <el-option label="扁平" value="扁平" />
              <el-option label="插画" value="插画" />
              <el-option label="节日" value="节日" />
            </el-select>

            <el-select v-model="filters.color" placeholder="颜色" clearable @change="loadThemes">
              <el-option label="蓝色" value="蓝色" />
              <el-option label="绿色" value="绿色" />
              <el-option label="红色" value="红色" />
              <el-option label="紫色" value="紫色" />
              <el-option label="黑色" value="黑色" />
              <el-option label="灰色" value="灰色" />
              <el-option label="黄色" value="黄色" />
              <el-option label="粉色" value="粉色" />
              <el-option label="橙色" value="橙色" />
            </el-select>

            <el-select v-model="filters.industry" placeholder="行业" clearable @change="loadThemes">
              <el-option label="科技互联网" value="科技互联网" />
              <el-option label="教育培训" value="教育培训" />
              <el-option label="政务" value="政务" />
              <el-option label="学院" value="学院" />
              <el-option label="电子商务" value="电子商务" />
              <el-option label="金融战略" value="金融战略" />
              <el-option label="法律" value="法律" />
              <el-option label="医疗健康" value="医疗健康" />
              <el-option label="文旅体育" value="文旅体育" />
              <el-option label="艺术广告" value="艺术广告" />
              <el-option label="人力资源" value="人力资源" />
              <el-option label="游戏娱乐" value="游戏娱乐" />
            </el-select>
          </div>

          <!-- 模板列表 -->
          <div class="template-list" v-loading="loadingThemes">
            <div
              v-for="theme in themes"
              :key="theme.templateIndexId"
              class="template-item"
              :class="{ selected: selectedTemplate === theme.templateIndexId }"
              @click="selectTemplate(theme)"
            >
              <img :src="theme.detailImage" :alt="theme.title" class="template-thumb" />
              <div class="template-info">
                <span class="template-title">{{ theme.title || '未命名模板' }}</span>
                <span class="template-pages">{{ theme.pageCount }}页</span>
              </div>
              <div class="template-selected-badge" v-if="selectedTemplate === theme.templateIndexId">
                <el-icon><Check /></el-icon>
              </div>
            </div>

            <div v-if="!loadingThemes && themes.length === 0" class="empty-templates">
              暂无可用模板，请尝试其他筛选条件
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：大纲预览和PPT生成进度 -->
      <div class="right-panel">
        <!-- 大纲预览卡片 -->
        <div class="card">
          <h3 class="card-title">大纲预览</h3>

          <div v-if="!outline && !loadingOutline" class="outline-placeholder">
            <el-empty description="请先填写左侧表单并生成大纲">
              <template #image>
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="1.5">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
              </template>
            </el-empty>
          </div>

          <div v-else-if="loadingOutline" class="outline-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>AI正在生成大纲...</span>
          </div>

          <div v-else class="outline-content">
            <!-- 标题和副标题 -->
            <div class="outline-header">
              <h2 class="outline-title">{{ outline?.title || form.title }}</h2>
              <p class="outline-subtitle" v-if="outline?.subTitle">{{ outline.subTitle }}</p>
            </div>

            <!-- 章节列表 -->
            <div class="chapter-list">
              <div
                v-for="(chapter, index) in outline?.chapters || []"
                :key="index"
                class="chapter-item"
              >
                <div class="chapter-header">
                  <span class="chapter-number">{{ index + 1 }}</span>
                  <span class="chapter-title">{{ chapter.chapterTitle }}</span>
                </div>
                <ul class="chapter-contents" v-if="chapter.chapterContents?.length">
                  <li v-for="(content, cIdx) in chapter.chapterContents" :key="cIdx">
                    {{ content }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="outline-actions">
              <el-button @click="regenerateOutline">重新生成大纲</el-button>
              <el-button type="primary" :loading="generatingPpt" @click="handleGeneratePpt">
                生成PPT
              </el-button>
            </div>
          </div>
        </div>

        <!-- PPT生成进度卡片 -->
        <div class="card" v-if="pptSid || generatingPpt">
          <h3 class="card-title">PPT生成进度</h3>

          <div v-if="generatingPpt && !pptStatus" class="ppt-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在提交PPT生成任务...</span>
          </div>

          <div v-else-if="pptStatus" class="ppt-progress">
            <!-- 进度条 -->
            <div class="progress-info">
              <span class="progress-status">
                {{ pptStatus.ppt_status === 'completed' ? '生成完成' : '生成中' }}
              </span>
              <span class="progress-pages">
                {{ pptStatus.done_pages || 0 }} / {{ pptStatus.total_pages || '?' }} 页
              </span>
            </div>

            <el-progress
              :percentage="calculatePercentage(pptStatus)"
              :status="pptStatus.ppt_status === 'completed' ? 'success' : undefined"
              :stroke-width="10"
            />

            <!-- AI配图状态 -->
            <div class="sub-task-status" v-if="pptStatus.ai_image_status">
              <span>AI配图：{{ pptStatus.ai_image_status === 'done' ? '已完成' : '生成中' }}</span>
            </div>

            <!-- 演讲备注状态 -->
            <div class="sub-task-status" v-if="pptStatus.card_note_status">
              <span>演讲备注：{{ pptStatus.card_note_status === 'done' ? '已完成' : '生成中' }}</span>
            </div>

            <!-- 下载按钮 -->
            <div class="ppt-download" v-if="pptStatus.ppt_status === 'completed' && pptStatus.ppt_url">
              <el-button type="success" size="large" @click="downloadPpt">
                <el-icon><Download /></el-icon>
                下载PPT
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Download, Loading } from '@element-plus/icons-vue'
import {
  getLessonPlanThemes,
  createLessonPlan,
  generateOutline,
  generatePpt,
  getPptStatus
} from '@/api/teacher/lesson_plan'

// 状态
const formRef = ref(null)
const loadingThemes = ref(false)
const loadingOutline = ref(false)
const generatingPpt = ref(false)
const generatingOutline = ref(false)
const outlineReady = ref(false)
const selectedTemplate = ref(null)
const themes = ref([])
const outline = ref(null)
const planId = ref(null)
const pptSid = ref(null)
const pptStatus = ref(null)
let pollTimer = null

// 表单数据
const form = reactive({
  title: '',
  courseName: '',
  knowledgePoints: '',
  targetAudience: '',
  teachingHours: 2
})

// 筛选器
const filters = reactive({
  style: '',
  color: '',
  industry: ''
})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入教案标题', trigger: 'blur' }],
  knowledgePoints: [
    { required: true, message: '请输入知识点描述', trigger: 'blur' },
    { min: 10, message: '知识点描述至少10个字', trigger: 'blur' }
  ]
}

// 加载PPT主题
async function loadThemes() {
  loadingThemes.value = true
  try {
    const params = {
      page: 1,
      page_size: 20
    }
    if (filters.style) params.style = filters.style
    if (filters.color) params.color = filters.color
    if (filters.industry) params.industry = filters.industry

    const res = await getLessonPlanThemes(params)
    // 后端返回 {success: true, data: {total, records}}，需要取 res.data.data.records
    themes.value = res.data?.data?.records || res.data?.records || res.records || []
  } catch (error) {
    console.error('[LessonPlan] 加载主题失败:', error)
    ElMessage.error('加载PPT模板失败')
  } finally {
    loadingThemes.value = false
  }
}

// 选择模板
function selectTemplate(theme) {
  selectedTemplate.value = theme.templateIndexId
}

// 生成大纲
async function handleGenerateOutline() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请完整填写必填项')
    return
  }

  loadingOutline.value = true
  generatingOutline.value = true

  try {
    // 先创建教案
    const createRes = await createLessonPlan({
      title: form.title,
      course_name: form.courseName,
      knowledge_points: form.knowledgePoints,
      target_audience: form.targetAudience,
      teaching_hours: form.teachingHours,
      template_id: selectedTemplate.value
    })

    planId.value = createRes.data?.id || createRes.id

    // 生成大纲
    const outlineRes = await generateOutline({
      plan_id: planId.value,
      knowledge_points: form.knowledgePoints
    })

    outline.value = outlineRes.data?.outline || outlineRes.outline
    outlineReady.value = true
    ElMessage.success('大纲生成成功')
  } catch (error) {
    console.error('[LessonPlan] 生成大纲失败:', error)
    ElMessage.error(error.message || '生成大纲失败')
  } finally {
    loadingOutline.value = false
    generatingOutline.value = false
  }
}

// 重新生成大纲
async function regenerateOutline() {
  outline.value = null
  outlineReady.value = false
  await handleGenerateOutline()
}

// 生成PPT
async function handleGeneratePpt() {
  if (!planId.value) {
    ElMessage.warning('请先生成大纲')
    return
  }

  generatingPpt.value = true
  pptSid.value = null
  pptStatus.value = null

  try {
    const res = await generatePpt({
      plan_id: planId.value,
      outline: outline.value,
      template_id: selectedTemplate.value,
      is_ai_image: false,
      ai_image_type: 'normal',
      is_card_note: false
    })

    pptSid.value = res.data?.sid || res.sid

    if (pptSid.value) {
      // 开始轮询状态
      startPolling()
    }
  } catch (error) {
    console.error('[LessonPlan] 生成PPT失败:', error)
    ElMessage.error(error.message || '生成PPT失败')
    generatingPpt.value = false
  }
}

// 轮询PPT状态
async function pollPptStatus() {
  if (!pptSid.value) return

  try {
    const res = await getPptStatus(pptSid.value)
    pptStatus.value = res.data || res

    if (pptStatus.value.ppt_status === 'completed' || pptStatus.value.ppt_status === 'done') {
      stopPolling()
      generatingPpt.value = false
      ElMessage.success('PPT生成完成！')
    } else if (pptStatus.value.ppt_status === 'build_failed') {
      stopPolling()
      generatingPpt.value = false
      ElMessage.error('PPT生成失败')
    }
  } catch (error) {
    console.error('[LessonPlan] 查询PPT状态失败:', error)
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollPptStatus, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 计算进度百分比
function calculatePercentage(status) {
  if (!status || !status.total_pages) return 0
  return Math.round((status.done_pages / status.total_pages) * 100)
}

// 下载PPT
function downloadPpt() {
  if (pptStatus.value?.ppt_url) {
    window.open(pptStatus.value.ppt_url, '_blank')
  }
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  outline.value = null
  outlineReady.value = false
  planId.value = null
  pptSid.value = null
  pptStatus.value = null
  stopPolling()
}

// 组件卸载时停止轮询
onUnmounted(() => {
  stopPolling()
})

// 页面加载时获取模板
onMounted(() => {
  loadThemes()
})
</script>

<style scoped>
.lesson-plan-page {
  min-height: calc(100vh - 64px);
  background: #F8FAFC;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 16px;
  color: #64748B;
  margin: 0;
}

.page-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .page-content {
    grid-template-columns: 1fr;
  }
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E2E8F0;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.form-actions .el-button {
  flex: 1;
}

/* 筛选器 */
.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.filter-row .el-select {
  flex: 1;
}

/* 模板列表 */
.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.template-item {
  position: relative;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-item:hover {
  border-color: #CBD5E1;
  transform: translateY(-2px);
}

.template-item.selected {
  border-color: #0891B2;
  box-shadow: 0 4px 12px rgba(8, 145, 178, 0.2);
}

.template-thumb {
  width: 100%;
  height: 90px;
  object-fit: cover;
  background: #F1F5F9;
}

.template-info {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.template-title {
  font-size: 12px;
  color: #1E293B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.template-pages {
  font-size: 11px;
  color: #94A3B8;
}

.template-selected-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: #0891B2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.empty-templates {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #94A3B8;
}

/* 大纲预览 */
.outline-placeholder,
.outline-loading,
.ppt-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #94A3B8;
  gap: 12px;
}

.outline-loading .el-icon,
.ppt-loading .el-icon {
  font-size: 32px;
}

.outline-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.outline-header {
  text-align: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.outline-title {
  font-size: 22px;
  font-weight: 600;
  color: #0891B2;
  margin: 0 0 8px;
}

.outline-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  background: #F8FAFC;
  border-radius: 12px;
  padding: 16px;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.chapter-number {
  width: 28px;
  height: 28px;
  background: #0891B2;
  color: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.chapter-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.chapter-contents {
  margin: 0;
  padding-left: 40px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chapter-contents li {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
}

.outline-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #E2E8F0;
}

/* PPT进度 */
.ppt-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-status {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
}

.progress-pages {
  font-size: 14px;
  color: #64748B;
}

.sub-task-status {
  font-size: 13px;
  color: #94A3B8;
  padding-left: 8px;
}

.ppt-download {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}

.ppt-download .el-button {
  padding: 12px 32px;
  font-size: 16px;
}
</style>
