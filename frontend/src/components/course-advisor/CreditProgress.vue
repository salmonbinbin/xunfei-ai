<template>
  <div class="credit-progress">
    <div class="progress-header">
      <h3 class="progress-title">学分进度</h3>
      <span class="progress-semester">{{ semester }}</span>
    </div>

    <div class="progress-main">
      <div class="progress-circle">
        <svg viewBox="0 0 100 100" class="progress-svg">
          <circle
            cx="50"
            cy="50"
            r="45"
            class="progress-bg"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            class="progress-fill"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="offset"
          />
        </svg>
        <div class="progress-text">
          <span class="progress-value">{{ percentage }}</span>
          <span class="progress-unit">%</span>
        </div>
      </div>

      <div class="progress-details">
        <div class="detail-item completed">
          <span class="detail-label">已完成</span>
          <span class="detail-value">{{ completed }}</span>
        </div>
        <div class="detail-item remaining">
          <span class="detail-label">剩余</span>
          <span class="detail-value">{{ remaining }}</span>
        </div>
        <div class="detail-item required">
          <span class="detail-label">毕业要求</span>
          <span class="detail-value">{{ required }}</span>
        </div>
      </div>
    </div>

    <div class="progress-bar-section">
      <div class="bar-header">
        <span>本学期目标学分</span>
        <span class="target-credits">{{ targetCredits }}学分</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: targetPercentage + '%' }" />
      </div>
    </div>

    <div v-if="suggestions.length > 0" class="suggestions">
      <div class="suggestion-title">选课建议</div>
      <div
        v-for="(s, index) in suggestions"
        :key="index"
        class="suggestion-item"
      >
        {{ s }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  completed: {
    type: Number,
    default: 0
  },
  required: {
    type: Number,
    default: 160
  },
  semester: {
    type: String,
    default: '2024-1'
  },
  targetCredits: {
    type: Number,
    default: 20
  },
  suggestions: {
    type: Array,
    default: () => []
  }
})

const percentage = computed(() => {
  return Math.round((props.completed / props.required) * 100)
})

const remaining = computed(() => Math.max(0, props.required - props.completed))

const circumference = 2 * Math.PI * 45
const offset = computed(() => {
  return circumference - (percentage.value / 100) * circumference
})

const targetPercentage = computed(() => {
  return Math.min(100, (props.targetCredits / props.required) * 100)
})
</script>

<style scoped>
.credit-progress {
  padding: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}

.progress-semester {
  font-size: 12px;
  color: #64748B;
  padding: 4px 10px;
  background: #F8FAFC;
  border-radius: 8px;
}

.progress-main {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}

.progress-circle {
  position: relative;
  width: 100px;
  height: 100px;
}

.progress-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-bg {
  fill: none;
  stroke: #E2E8F0;
  stroke-width: 8;
}

.progress-fill {
  fill: none;
  stroke: #0891B2;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-value {
  font-size: 24px;
  font-weight: 700;
  color: #0891B2;
}

.progress-unit {
  font-size: 12px;
  color: #64748B;
}

.progress-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #F8FAFC;
  border-radius: 8px;
}

.detail-item.completed .detail-value {
  color: #059669;
  font-weight: 600;
}

.detail-item.remaining .detail-value {
  color: #F59E0B;
  font-weight: 600;
}

.detail-item.required .detail-value {
  color: #64748B;
}

.detail-label {
  font-size: 12px;
  color: #64748B;
}

.progress-bar-section {
  padding: 12px;
  background: #F8FAFC;
  border-radius: 12px;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #64748B;
}

.target-credits {
  font-weight: 600;
  color: #0891B2;
}

.bar-track {
  height: 8px;
  background: #E2E8F0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0891B2, #22D3EE);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.suggestions {
  margin-top: 16px;
  padding: 12px;
  background: rgba(8, 145, 178, 0.05);
  border-radius: 12px;
}

.suggestion-title {
  font-size: 12px;
  font-weight: 600;
  color: #0891B2;
  margin-bottom: 8px;
}

.suggestion-item {
  font-size: 12px;
  color: #475569;
  padding: 4px 0;
  border-bottom: 1px solid rgba(8, 145, 178, 0.1);
}

.suggestion-item:last-child {
  border-bottom: none;
}
</style>