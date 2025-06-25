<template>
  <canvas
    ref="canvasRef"
    class="image-canvas"
    @mousedown="onMouseDown"
    @mouseup="onMouseUp"
  ></canvas>
</template>

<script setup>
import { ref } from 'vue'

const canvasRef = ref(null)

const props = defineProps({
  previewUrl: {
    type: String,
    default: ''
  },
  crop: {
    type: Object,
    default: () => ({ x: 0, y: 0, w: 0, h: 0 })
  }
})

const emit = defineEmits(['mouse-down', 'mouse-up', 'crop-change'])

function onMouseDown(event) {
  emit('mouse-down', event)
}

function onMouseUp(event) {
  emit('mouse-up', event)
}

defineExpose({
  canvasRef
})
</script>

<style scoped>
.image-canvas {
  margin: 0.7rem 0;
  width: 100%;
  max-width: 340px;
  max-height: 340px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #f8fafc;
  box-shadow: 0 2px 8px 0 rgba(60, 60, 60, 0.04);
  display: block;
  cursor: crosshair;
}

.image-canvas:hover {
  border-color: #42b983;
}
</style>
