<template>
  <div class="placeholder-page">
    <div class="placeholder-icon">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </div>
    <h2 class="placeholder-title">通知发布</h2>
    <p class="placeholder-desc">AI智能通知生成功能开发中</p>
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
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(167, 139, 250, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8B5CF6;
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
