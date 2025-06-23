<script setup>
import { ref } from 'vue'
import AppLayout from './components/Layout/AppLayout.vue'
import DatasetOverview from './components/DatasetOverview/DatasetOverview.vue'
import IndexBuilder from './components/IndexBuilder/IndexBuilder.vue'
import ImageSearch from './components/ImageSearch/ImageSearch.vue'
import DuplicateDetector from './components/DuplicateDetector/DuplicateDetector.vue'

// 当前活动的模块
const activeModule = ref('overview')

// 导航项
const navigationItems = [
  { id: 'overview', label: '数据集概览', icon: '📊' },
  { id: 'search', label: '图片检索', icon: '🔍' },
  { id: 'index', label: '索引管理', icon: '🏗️' },
  { id: 'duplicate', label: '重复检测', icon: '🎯' }
]

// 切换模块
const switchModule = (moduleId) => {
  activeModule.value = moduleId
}
</script>

<template>
  <div class="app">
    <!-- 导航栏 -->
    <nav class="app-nav" v-if="activeModule !== 'overview'">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>浮图图片检索系统</h1>
        </div>
        <div class="nav-menu">
          <button 
            v-for="item in navigationItems" 
            :key="item.id"
            class="nav-item"
            :class="{ active: activeModule === item.id }"
            @click="switchModule(item.id)"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- 数据集概览页面 -->
    <DatasetOverview 
      v-if="activeModule === 'overview'"
      @navigate="switchModule"
    />
    
    <!-- 其他功能模块 -->
    <AppLayout v-if="activeModule !== 'overview'">
      <div class="app-content">
        <!-- 索引构建模块 -->
        <IndexBuilder v-if="activeModule === 'index'" />
        
        <!-- 图片检索模块 -->
        <ImageSearch v-if="activeModule === 'search'" />
        
        <!-- 重复图片检测模块 -->
        <DuplicateDetector v-if="activeModule === 'duplicate'" />
      </div>
    </AppLayout>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 导航栏样式 */
.app-nav {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.nav-menu {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.nav-item:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.nav-item.active {
  background: #667eea;
  color: white;
}

.nav-icon {
  font-size: 1.1rem;
}

.nav-label {
  font-weight: 500;
}

.app-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-item {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .app-content {
    gap: 1rem;
    padding: 1rem;
  }
}
</style>
