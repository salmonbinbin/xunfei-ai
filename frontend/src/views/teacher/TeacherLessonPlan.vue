<template>
  <div class="placeholder-page">
    <div class="placeholder-icon">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
      </svg>
    </div>
    <h2 class="placeholder-title">备课教案</h2>
    <p class="placeholder-desc">AI智能教案生成功能开发中</p>
    <el-tag type="warning" effect="plain" size="large">待开发</el-tag>
  </div>
</template>

<script setup>
</script>

<style scoped>
.placeholder-page {
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #F8FAFC;
}

.placeholder-icon {
  width: 120px;
  height: 120px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.08), rgba(52, 211, 153, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #059669;
  margin-bottom: 24px;
}

.placeholder-title {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px;
}

.placeholder-desc {
  font-size: 16px;
  color: #64748B;
  margin: 0 0 20px;
}
</style>
