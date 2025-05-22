<script setup>
import TheWelcome from './components/TheWelcome.vue'
</script>

<template>
  <main class="main-center">
    <TheWelcome />
  </main>
</template>

<style scoped>
.main-center {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background-soft);
}
</style>
