<template>
  <div class="placeholder-page">
    <div class="placeholder-icon">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </svg>
    </div>
    <h2 class="placeholder-title">成绩管理</h2>
    <p class="placeholder-desc">智能成绩分析功能开发中</p>
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
  background: linear-gradient(135deg, rgba(8, 145, 178, 0.08), rgba(34, 211, 238, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0891B2;
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
