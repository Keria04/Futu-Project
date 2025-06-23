<template>
  <div class="message-display" :class="messageClass">
    <slot>{{ message }}</slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info', // info, success, warning, error
    validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
  }
})

const messageClass = computed(() => {
  return `message-${props.type}`
})
</script>

<style scoped>
.message-display {
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  border-radius: 6px;
  font-size: 1rem;
  min-height: 1.2em;
  display: flex;
  align-items: center;
}

.message-info {
  background: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #2196f3;
}

.message-success {
  background: #e8f5e8;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.message-warning {
  background: #fff3e0;
  color: #f57c00;
  border-left: 4px solid #ff9800;
}

.message-error {
  background: #ffebee;
  color: #d32f2f;
  border-left: 4px solid #f44336;
}
</style>
