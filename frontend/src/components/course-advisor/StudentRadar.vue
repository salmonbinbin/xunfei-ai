<template>
  <div class="student-radar">
    <div class="radar-header">
      <h3 class="radar-title">学习力分析</h3>
    </div>

    <!-- 能力偏向选择 -->
    <div class="ability-selector">
      <span class="selector-label">能力偏向</span>
      <div class="ability-options">
        <button
          v-for="type in abilityTypes"
          :key="type.value"
          class="ability-btn"
          :class="{ active: selectedAbility === type.value }"
          @click="onAbilityChange(type.value)"
        >
          <span class="ability-icon">{{ type.icon }}</span>
          <span class="ability-text">{{ type.label }}</span>
        </button>
      </div>
    </div>

    <!-- 两个进度环 -->
    <div class="progress-rings">
      <div class="ring-item">
        <div class="ring-container">
          <svg viewBox="0 0 100 100" class="ring-svg">
            <circle cx="50" cy="50" r="40" class="ring-bg" />
            <circle
              cx="50"
              cy="50"
              r="40"
              class="ring-fill cyan"
              :stroke-dasharray="getCircleDasharray(majorPercent)"
            />
          </svg>
          <div class="ring-content">
            <span class="ring-value">{{ majorPercent }}%</span>
          </div>
        </div>
        <span class="ring-label">专业知识覆盖</span>
        <span class="ring-desc">基于已修课程计算</span>
      </div>

      <div class="ring-item">
        <div class="ring-container">
          <svg viewBox="0 0 100 100" class="ring-svg">
            <circle cx="50" cy="50" r="40" class="ring-bg" />
            <circle
              cx="50"
              cy="50"
              r="40"
              class="ring-fill purple"
              :stroke-dasharray="getCircleDasharray(goalPercent)"
            />
          </svg>
          <div class="ring-content">
            <span class="ring-value">{{ goalPercent }}%</span>
          </div>
        </div>
        <span class="ring-label">目标匹配度</span>
        <span class="ring-desc">{{ goalText }}</span>
      </div>
    </div>

    <!-- 学生信息 -->
    <div class="student-info">
      <div class="info-row">
        <span class="info-label">专业</span>
        <span class="info-value">{{ profileData.major || '计算机科学与技术' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">年级</span>
        <span class="info-value">{{ profileData.grade || 2 }}年级</span>
      </div>
      <div class="info-row">
        <span class="info-label">目标</span>
        <span class="info-value goal-badge" :class="goalClass">{{ profileData.goal || '未设定' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  radarData: {
    type: Object,
    required: true
  },
  abilityType: {
    type: String,
    default: '逻辑型'
  },
  profileData: {
    type: Object,
    default: () => ({
      major: '',
      grade: 0,
      goal: ''
    })
  }
})

const emit = defineEmits(['update:abilityType'])

const abilityTypes = [
  { value: '逻辑型', label: '逻辑型', icon: '🧠' },
  { value: '记忆型', label: '记忆型', icon: '📖' },
  { value: '创意型', label: '创意型', icon: '💡' }
]

const selectedAbility = computed(() => props.abilityType)

const majorPercent = computed(() => props.radarData?.['专业知识覆盖度'] || 0)
const goalPercent = computed(() => props.radarData?.['目标匹配度'] || 0)

const goalText = computed(() => {
  const goal = props.profileData?.goal || ''
  const texts = {
    '考研': '与考研方向匹配',
    '考公': '与考公方向匹配',
    '就业': '与就业方向匹配',
    '出国': '与出国方向匹配'
  }
  return texts[goal] || '暂无明确目标'
})

const goalClass = computed(() => {
  const goal = props.profileData?.goal || ''
  return {
    '考研': 'goal-kaoyan',
    '考公': 'goal-kaogong',
    '就业': 'goal-jiuye',
    '出国': 'goal-chuguo'
  }[goal] || ''
})

function getCircleDasharray(percent) {
  const circumference = 2 * Math.PI * 40
  const arc = (percent / 100) * circumference
  return `${arc} ${circumference}`
}

function onAbilityChange(type) {
  emit('update:abilityType', type)
}
</script>

<style scoped>
.student-radar {
  padding: 16px;
}

.radar-header {
  margin-bottom: 12px;
}

.radar-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}

.ability-selector {
  margin-bottom: 20px;
}

.selector-label {
  display: block;
  font-size: 12px;
  color: #64748B;
  margin-bottom: 8px;
}

.ability-options {
  display: flex;
  gap: 8px;
}

.ability-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 8px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ability-btn.active {
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  border-color: #0891B2;
  color: #fff;
}

.ability-icon {
  font-size: 18px;
}

.ability-text {
  font-size: 11px;
  font-weight: 500;
}

.progress-rings {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.ring-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.ring-container {
  position: relative;
  width: 90px;
  height: 90px;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #E2E8F0;
  stroke-width: 8;
}

.ring-fill {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.ring-fill.cyan {
  stroke: #0891B2;
}

.ring-fill.purple {
  stroke: #8B5CF6;
}

.ring-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.ring-value {
  font-size: 18px;
  font-weight: 700;
  color: #1E293B;
}

.ring-label {
  font-size: 12px;
  font-weight: 600;
  color: #1E293B;
}

.ring-desc {
  font-size: 10px;
  color: #94A3B8;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #F8FAFC;
  border-radius: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.info-label {
  color: #64748B;
}

.info-value {
  font-weight: 500;
  color: #1E293B;
}

.goal-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.goal-kaoyan {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.goal-kaogong {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.goal-jiuye {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.goal-chuguo {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}
</style>
