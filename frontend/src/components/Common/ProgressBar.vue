<template>
  <div v-if="isVisible" class="progress-container">
    <div class="progress-bar">
      <div 
        class="progress-inner" 
        :style="{ width: progress + '%' }"
      ></div>
    </div>
    <div class="progress-text">
      进度: {{ progress }}%
      <span v-if="status" class="progress-status">{{ status }}</span>
    </div>
  </div>
</template>

<!-- 123 -->

<script setup>
defineProps({
  progress: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    default: ''
  },
  isVisible: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.progress-container {
  width: 100%;
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 16px;
  background: #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.progress-inner {
  height: 100%;
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}

.progress-status {
  margin-left: 0.5rem;
  color: #42b983;
}
</style>
