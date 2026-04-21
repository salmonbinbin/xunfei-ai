<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-deep-space/80 backdrop-blur-sm"
      >
        <div class="text-center">
          <div class="relative w-20 h-20 mx-auto mb-4">
            <div class="absolute inset-0 border-4 border-neon-purple/20 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-transparent border-t-neon-purple rounded-full animate-spin"></div>
            <div class="absolute inset-2 border-4 border-transparent border-t-neon-purple-light rounded-full animate-spin-reverse"></div>
          </div>
          <p v-if="text" class="text-text-body">{{ text }}</p>
          <p v-else class="text-text-body">加载中...</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes spin-reverse {
  to {
    transform: rotate(-360deg);
  }
}

.animate-spin-reverse {
  animation: spin-reverse 1.5s linear infinite;
}
</style>
