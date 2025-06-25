<script setup>
import { ref } from 'vue'
import AppLayoutWithNav from './components/Layout/AppLayoutWithNav.vue'
import DatasetOverview from './components/DatasetOverview/DatasetOverview.vue'
import IndexBuilder from './components/IndexBuilder/IndexBuilder.vue'
import ImageSearch from './components/ImageSearch/ImageSearch.vue'
import DuplicateDetector from './components/DuplicateDetector/DuplicateDetector.vue'

// 当前视图
const currentView = ref('datasets')

// 切换视图
const handleViewChange = (view) => {
  currentView.value = view
}
</script>

<template>
  <AppLayoutWithNav @view-change="handleViewChange">
    <!-- 数据集概览 -->
    <DatasetOverview v-if="currentView === 'datasets'" />
    
    <!-- 图片检索 -->
    <div v-else-if="currentView === 'search'" class="module-container">
      <ImageSearch />
    </div>
    
    <!-- 索引构建 -->
    <div v-else-if="currentView === 'index'" class="module-container">
      <IndexBuilder />
    </div>
    
    <!-- 重复检测 -->
    <div v-else-if="currentView === 'duplicate'" class="module-container">
      <DuplicateDetector />
    </div>
  </AppLayoutWithNav>
</template>

<style scoped>
.module-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 80px);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .module-container {
    padding: 1rem;
    margin-top: 1rem;
  }
}
</style>