<template>
  <div class="course-card card-cyber card-hover cursor-pointer" @click="$emit('click')">
    <div class="flex items-start justify-between mb-2">
      <div>
        <h3 class="text-lg font-semibold text-text-primary">{{ course.name }}</h3>
        <p class="text-sm text-text-secondary mt-1">{{ course.teacher }}</p>
      </div>
      <span class="badge-cyber">{{ course.day_name }}</span>
    </div>

    <div class="flex items-center gap-4 text-sm text-text-secondary mt-3">
      <div class="flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ course.start_time }} - {{ course.end_time }}</span>
      </div>
      <div class="flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span>{{ course.location }}</span>
      </div>
    </div>

    <div v-if="course.note" class="mt-3 text-xs text-text-disabled italic">
      {{ course.note }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  course: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])
</script>
