<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-container">
        <h1 class="app-title">浮图图片检索系统</h1>
        
        <nav class="app-nav">
          <button 
            class="nav-button"
            :class="{ active: currentView === 'datasets' }"
            @click="switchView('datasets')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
            数据集概览
          </button>
          
          <button 
            class="nav-button"
            :class="{ active: currentView === 'search' }"
            @click="switchView('search')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            图片检索
          </button>
          
          <button 
            class="nav-button"
            :class="{ active: currentView === 'duplicate' }"
            @click="switchView('duplicate')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
            </svg>
            重复检测
          </button>
        </nav>
      </div>
    </header>
    
    <!-- 主要内容区域 -->
    <main class="app-main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 当前视图
const currentView = ref('datasets')

// 发射事件
const emit = defineEmits(['view-change'])

// 切换视图
const switchView = (view) => {
  currentView.value = view
  emit('view-change', view)
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 顶部导航栏 */
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* 导航按钮 */
.app-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-button:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.nav-button.active {
  background: #667eea;
  color: white;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

/* 主要内容区域 */
.app-main {
  flex: 1;
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .app-title {
    font-size: 1.25rem;
  }
  
  .app-nav {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .nav-icon {
    width: 16px;
    height: 16px;
  }
}
</style>
