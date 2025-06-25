<template>
  <div class="app-layout">
    <header class="app-header">
      <h1 class="app-title">浮图 - 图片检索系统</h1>
      <p class="app-subtitle">智能图片搜索与重复检测平台</p>
    </header>
    
    <main class="app-main">
      <div class="container">
        <slot />
      </div>
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2025 浮图图片检索系统. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
// 主布局组件，提供统一的页面结构
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 2rem 0;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 300;
}

.app-main {
  flex: 1;
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-footer {
  background: rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.app-footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .app-title {
    font-size: 2rem;
  }
  
  .app-subtitle {
    font-size: 1rem;
  }
  
  .app-main {
    padding: 1rem 0;
  }
  
  .container {
    padding: 0 0.5rem;
  }
}
</style>
