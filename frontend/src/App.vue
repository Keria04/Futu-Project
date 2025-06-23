<script setup>
import AppLayout from './components/Layout/AppLayout.vue'
import IndexBuilder from './components/IndexBuilder/IndexBuilder.vue'
import ImageSearch from './components/ImageSearch/ImageSearch.vue'
import DuplicateDetector from './components/DuplicateDetector/DuplicateDetector.vue'
</script>

<template>
  <AppLayout>
    <div class="app-content">
      <!-- 索引构建模块 -->
      <IndexBuilder />
      
      <!-- 图片检索模块 -->
      <ImageSearch />
      
      <!-- 重复图片检测模块 -->
      <DuplicateDetector />
    </div>
  </AppLayout>
</template>

<style scoped>
.app-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

@media (max-width: 768px) {
  .app-content {
    gap: 1rem;
  }
}
</style>
