<script setup>
import TheWelcome from './components/TheWelcome.vue'
</script>

<template>
  <div class="app-bg">
    <header class="header-bar">
      <span class="header-title">智能图片检索系统</span>
      <span class="header-desc">支持多数据集</span>
    </header>
    <main class="main-center">
      <TheWelcome />
    </main>
    <footer class="footer-bar">
      <span>© 2025 Futu-Project | Futu保留所有权利</span>
    </footer>
  </div>
</template>

<style scoped>
.app-bg {
  min-height: 100vh;
  background: linear-gradient(120deg, #e3f0ff 0%, #f8fcff 100%);
  display: flex;
  flex-direction: column;
}
.header-bar {
  width: 100%;
  height: 70px;
  background: rgba(255,255,255,0.95);
  box-shadow: 0 2px 16px 0 rgba(60,60,60,0.07);
  display: flex;
  align-items: center;
  padding: 0 1.2vw;
  gap: 1em;
  position: sticky;
  top: 0;
  z-index: 10;
}
.logo {
  height: 38px;
  margin-right: 0.7em;
}
.header-title {
  font-size: 1.18rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 1.5px;
}
.header-desc {
  margin-left: auto;
  color: #5c6b7a;
  font-size: 0.98rem;
  font-weight: 400;
  opacity: 0.85;
}
.main-center {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0 0 0 0;
}
.footer-bar {
  width: 100%;
  text-align: center;
  color: #8ca2b3;
  font-size: 0.98em;
  padding: 0.8em 0 0.7em 0;
  background: transparent;
  letter-spacing: 1px;
}
@media (max-width: 500px) {
  .header-bar {
    flex-direction: column;
    height: auto;
    padding: 0.5em 0.5em;
    gap: 0.5em;
    align-items: flex-start;
  }
  .main-center {
    padding: 1vw 0 0.5vw 0;
  }
}
</style>