<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

onMounted(() => {
  appStore.detectDevice()
  window.addEventListener('resize', appStore.detectDevice)
})
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
