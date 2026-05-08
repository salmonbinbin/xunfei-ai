<template>
  <div class="teacher-home">
    <main class="main-content">
      <!-- 问候区 -->
      <section class="greeting-block">
        <p class="greeting-date">{{ currentDate }}</p>
        <h1 class="greeting-title">{{ greetingText }}，{{ userStore.userInfo?.name || '老师' }}</h1>
        <p class="greeting-subtitle">选择下方功能模块，开启您的智能教学之旅。AI将协助您完成成绩分析、通知发布、教案生成等工作。</p>
      </section>

      <!-- 功能模块标题 -->
      <h2 class="section-title">教学功能</h2>

      <!-- 功能模块卡片 -->
      <div class="modules-grid">
        <!-- 成绩管理 -->
        <div class="module-card card-grade" @click="handleCardClick('grade')">
          <div class="module-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <h3 class="module-title">成绩管理</h3>
          <p class="module-desc">上传学生成绩表，AI智能分析成绩分布，生成统计图表与教学建议报告</p>
          <div class="module-tags">
            <span class="module-tag">智能分析</span>
            <span class="module-tag">可视化</span>
            <span class="module-tag">导出</span>
          </div>
        </div>

        <!-- 通知发布 -->
        <div class="module-card card-notification" @click="handleCardClick('notification')">
          <div class="module-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <h3 class="module-title">通知发布</h3>
          <p class="module-desc">输入通知要点，AI生成格式规范的通知文档，支持一键推送到飞书群</p>
          <div class="module-tags">
            <span class="module-tag">AI生成</span>
            <span class="module-tag">格式规范</span>
            <span class="module-tag">飞书推送</span>
          </div>
        </div>

        <!-- 备课教案 -->
        <div class="module-card card-lesson" @click="handleCardClick('lesson-plan')">
          <div class="module-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <h3 class="module-title">备课教案</h3>
          <p class="module-desc">描述课程知识点，AI生成结构化教学大纲与精美PPT演示文稿</p>
          <div class="module-tags">
            <span class="module-tag">AI大纲</span>
            <span class="module-tag">PPT</span>
            <span class="module-tag">教学建议</span>
          </div>
        </div>
      </div>

      <!-- 底部引言 -->
      <section class="quote-section">
        <p class="quote-text" :style="{ opacity: quoteOpacity }">{{ currentQuote.text }}</p>
        <p class="quote-author" :style="{ opacity: quoteOpacity }">{{ currentQuote.author }}</p>
        <button class="quote-refresh" @click="refreshQuote" title="换一句">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 教育名言
const quotes = [
  { text: "教育不是注满一桶水，而是点燃一把火。", author: "威廉·巴赫·叶芝" },
  { text: "教育的本质是一棵树摇动另一棵树，一朵云推动另一朵云，一个灵魂唤醒另一个灵魂。", author: "卡尔·雅斯贝尔斯" },
  { text: "教而不研则浅，研而不教则空。", author: "陶行知" },
  { text: "捧着一颗心来，不带半根草去。", author: "陶行知" },
  { text: "教师是人类灵魂的工程师。", author: "米哈伊尔·加里宁" },
  { text: "教学的艺术不在于传授本领，而在于激励、唤醒和鼓舞。", author: "第斯多惠" },
  { text: "没有爱就没有教育。", author: "陶行知" },
  { text: "真教育是心心相印的活动，唯独从心里发出来，才能打动心灵的深处。", author: "陶行知" },
  { text: "千教万教教人求真，千学万学学做真人。", author: "陶行知" },
  { text: "先生不应该专教书，他的责任是教人做人。", author: "陶行知" },
  { text: "好的先生不是教书，不是教学生，乃是教学生学。", author: "陶行知" },
  { text: "教育是什么？就单方面讲，需一句话，就是养成良好的习惯。", author: "叶圣陶" },
  { text: "教是为了不需要教。", author: "叶圣陶" },
  { text: "师者，所以传道受业解惑也。", author: "韩愈" },
  { text: "师者，人之模范也。", author: "扬雄" },
  { text: "古之学者必严其师，师严然后道尊。", author: "欧阳修" },
  { text: "教育植根于爱。", author: "鲁迅" },
  { text: "学而不思则罔，思而不学则殆。", author: "孔子" },
  { text: "知之者不如好之者，好之者不如乐之者。", author: "孔子" },
  { text: "三人行，必有我师焉。择其善者而从之，其不善者而改之。", author: "孔子" },
  { text: "学而时习之，不亦说乎？", author: "孔子" },
  { text: "温故而知新，可以为师矣。", author: "孔子" },
  { text: "不愤不启，不悱不发。举一隅不以三隅反，则不复也。", author: "孔子" },
  { text: "教师是太阳底下最光辉的职业。", author: "夸美纽斯" },
  { text: "教育者，养成人格之事业也。", author: "蔡元培" },
  { text: "知教育者，与其守成法，毋宁尚自然；与其求划一，毋宁展个性。", author: "蔡元培" },
  { text: "活得的人才教育不是灌输知识，而是将开发文化宝库的钥匙交给学生。", author: "陶行知" }
]

const currentQuote = ref(quotes[0])
const quoteOpacity = ref(1)
const lastIndex = ref(-1)

// 计算当前日期
const currentDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1
  const day = now.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekday = weekdays[now.getDay()]
  return `${year}年${month}月${day}日 · ${weekday}`
})

// 计算问候语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 获取随机名言
function getRandomQuote() {
  let newIndex
  do {
    newIndex = Math.floor(Math.random() * quotes.length)
  } while (newIndex === lastIndex.value && quotes.length > 1)
  lastIndex.value = newIndex
  return quotes[newIndex]
}

// 刷新名言（带淡入淡出效果）
function refreshQuote() {
  quoteOpacity.value = 0
  setTimeout(() => {
    currentQuote.value = getRandomQuote()
    quoteOpacity.value = 1
  }, 200)
}

// 页面加载时获取用户信息并随机选择名言
onMounted(() => {
  // 确保用户信息已加载
  if (!userStore.userInfo) {
    userStore.fetchUser()
  }
  // 随机选择一条名言
  currentQuote.value = getRandomQuote()
})

// 跳转到功能页面
function handleCardClick(type) {
  router.push(`/teacher/${type}`)
}
</script>

<style scoped>
.teacher-home {
  min-height: 100vh;
  background: var(--bg-page, #F8FAFC);
}

.main-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 40px 60px;
}

/* 问候区 */
.greeting-block {
  margin-bottom: 40px;
}

.greeting-date {
  font-size: 13px;
  color: var(--primary, #0891B2);
  margin-bottom: 8px;
  font-weight: 500;
}

.greeting-title {
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary, #1E293B);
  line-height: 1.3;
  margin: 0 0 12px;
}

.greeting-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #64748B);
  max-width: 520px;
  line-height: 1.6;
  margin: 0;
}

/* 功能模块标题 */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary, #64748B);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border, #E2E8F0);
}

/* 功能模块卡片 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.module-card {
  background: var(--bg-card, #FFFFFF);
  border: 1px solid var(--border, #E2E8F0);
  border-radius: 16px;
  padding: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-grade::before { background: linear-gradient(90deg, var(--primary, #0891B2), #22D3EE); }
.card-notification::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }
.card-lesson::before { background: linear-gradient(90deg, #059669, #34D399); }

.module-card:hover::before {
  opacity: 1;
}

.module-card:hover {
  border-color: var(--primary, #0891B2);
  box-shadow: 0 8px 24px rgba(8, 145, 178, 0.1);
  transform: translateY(-2px);
}

.module-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.card-grade .module-icon {
  background: rgba(8, 145, 178, 0.1);
}
.card-grade .module-icon svg { color: var(--primary, #0891B2); }

.card-notification .module-icon {
  background: rgba(139, 92, 246, 0.1);
}
.card-notification .module-icon svg { color: #8B5CF6; }

.card-lesson .module-icon {
  background: rgba(5, 150, 105, 0.1);
}
.card-lesson .module-icon svg { color: #059669; }

.module-icon svg {
  width: 26px;
  height: 26px;
}

.module-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1E293B);
  margin: 0 0 8px;
}

.module-desc {
  font-size: 13px;
  color: var(--text-muted, #94A3B8);
  line-height: 1.6;
  margin: 0 0 16px;
}

.module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.module-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--bg-warm, #F1F5F9);
  color: var(--text-secondary, #64748B);
}

/* 底部引言 */
.quote-section {
  background: rgba(8, 145, 178, 0.04);
  border: 1px solid rgba(8, 145, 178, 0.12);
  border-radius: 16px;
  padding: 32px 40px;
  text-align: center;
  position: relative;
  transition: opacity 0.2s ease;
}

.quote-text {
  font-size: 17px;
  color: var(--text-primary, #1E293B);
  line-height: 1.8;
  font-style: italic;
  margin: 0 0 12px;
  transition: opacity 0.2s ease;
}

.quote-author {
  font-size: 13px;
  color: var(--primary, #0891B2);
  font-weight: 500;
  margin: 0;
  transition: opacity 0.2s ease;
}

.quote-refresh {
  position: absolute;
  bottom: 14px;
  right: 16px;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: rgba(8, 145, 178, 0.08);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.quote-refresh:hover {
  background: rgba(8, 145, 178, 0.15);
}

.quote-refresh svg {
  width: 14px;
  height: 14px;
  color: var(--primary, #0891B2);
}

/* 响应式 */
@media (max-width: 900px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }

  .main-content {
    padding: 24px 20px 40px;
  }

  .greeting-title {
    font-size: 24px;
  }
}
</style>
