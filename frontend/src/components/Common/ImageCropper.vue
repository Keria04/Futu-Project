<template>
  <div class="image-cropper">
    <div class="cropper-container">
      <div class="image-wrapper" ref="imageWrapperRef">
        <img 
          ref="imageRef"
          :src="imageUrl" 
          @load="initCropper"
          @mousedown="startCrop"
          @mousemove="updateCrop"
          @mouseup="endCrop"
          @mouseleave="endCrop"
          class="cropper-image"
        />
        <div 
          v-if="showCropArea"
          class="crop-overlay"
          :style="overlayStyle"
        >
          <div class="crop-area" :style="cropAreaStyle">
            <div class="crop-handles">
              <div class="handle handle-nw"></div>
              <div class="handle handle-ne"></div>
              <div class="handle handle-sw"></div>
              <div class="handle handle-se"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="cropper-controls">
      <button 
        class="btn btn-secondary" 
        @click="resetCrop"
        :disabled="!showCropArea"
      >
        重置框选
      </button>
      <button 
        class="btn btn-primary" 
        @click="confirmCrop"
        :disabled="!showCropArea"
      >
        确认框选
      </button>
    </div>
    
    <!-- 框选后的预览 -->
    <div v-if="croppedImageUrl" class="cropped-preview">
      <h4>框选区域预览</h4>
      <img :src="croppedImageUrl" class="preview-image" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['crop-change', 'cropped-image'])

// 组件引用
const imageRef = ref(null)
const imageWrapperRef = ref(null)

// 状态
const isCropping = ref(false)
const showCropArea = ref(false)
const croppedImageUrl = ref('')

// 裁剪区域数据
const cropData = ref({
  x: 0,
  y: 0,
  width: 0,
  height: 0
})

// 图片尺寸
const imageSize = ref({
  width: 0,
  height: 0,
  displayWidth: 0,
  displayHeight: 0
})

// 计算样式
const overlayStyle = computed(() => ({
  position: 'absolute',
  top: '0',
  left: '0',
  width: '100%',
  height: '100%',
  backgroundColor: 'rgba(0, 0, 0, 0.3)',
  pointerEvents: 'none'
}))

const cropAreaStyle = computed(() => {
  if (!showCropArea.value) return {}
  
  const scaleX = imageSize.value.displayWidth / imageSize.value.width
  const scaleY = imageSize.value.displayHeight / imageSize.value.height
  
  return {
    position: 'absolute',
    left: `${cropData.value.x * scaleX}px`,
    top: `${cropData.value.y * scaleY}px`,
    width: `${cropData.value.width * scaleX}px`,
    height: `${cropData.value.height * scaleY}px`,
    backgroundColor: 'transparent',
    border: '2px solid #42b983',
    boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.3)',
    pointerEvents: 'none'
  }
})

// 初始化裁剪器
function initCropper() {
  const img = imageRef.value
  if (!img) return
  
  imageSize.value = {
    width: img.naturalWidth,
    height: img.naturalHeight,
    displayWidth: img.offsetWidth,
    displayHeight: img.offsetHeight
  }
}

// 开始裁剪
function startCrop(event) {
  event.preventDefault()
  
  const rect = imageRef.value.getBoundingClientRect()
  const scaleX = imageSize.value.width / imageSize.value.displayWidth
  const scaleY = imageSize.value.height / imageSize.value.displayHeight
  
  const x = (event.clientX - rect.left) * scaleX
  const y = (event.clientY - rect.top) * scaleY
  
  cropData.value = {
    x: Math.max(0, x),
    y: Math.max(0, y),
    width: 0,
    height: 0
  }
  
  isCropping.value = true
  showCropArea.value = false
}

// 更新裁剪区域
function updateCrop(event) {
  if (!isCropping.value) return
  
  event.preventDefault()
  
  const rect = imageRef.value.getBoundingClientRect()
  const scaleX = imageSize.value.width / imageSize.value.displayWidth
  const scaleY = imageSize.value.height / imageSize.value.displayHeight
  
  const currentX = (event.clientX - rect.left) * scaleX
  const currentY = (event.clientY - rect.top) * scaleY
  
  const width = Math.abs(currentX - cropData.value.x)
  const height = Math.abs(currentY - cropData.value.y)
  
  cropData.value.width = Math.min(width, imageSize.value.width - cropData.value.x)
  cropData.value.height = Math.min(height, imageSize.value.height - cropData.value.y)
  
  if (cropData.value.width > 10 && cropData.value.height > 10) {
    showCropArea.value = true
  }
}

// 结束裁剪
function endCrop() {
  if (!isCropping.value) return
  
  isCropping.value = false
  
  if (cropData.value.width < 10 || cropData.value.height < 10) {
    showCropArea.value = false
    return
  }
  
  // 发送裁剪数据
  emit('crop-change', {
    x: Math.round(cropData.value.x),
    y: Math.round(cropData.value.y),
    w: Math.round(cropData.value.width),
    h: Math.round(cropData.value.height)
  })
}

// 重置裁剪
function resetCrop() {
  showCropArea.value = false
  croppedImageUrl.value = ''
  cropData.value = { x: 0, y: 0, width: 0, height: 0 }
  emit('crop-change', { x: 0, y: 0, w: 0, h: 0 })
}

// 确认裁剪
async function confirmCrop() {
  if (!showCropArea.value) return
  
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    canvas.width = cropData.value.width
    canvas.height = cropData.value.height
    
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      ctx.drawImage(
        img,
        cropData.value.x,
        cropData.value.y,
        cropData.value.width,
        cropData.value.height,
        0,
        0,
        cropData.value.width,
        cropData.value.height
      )
      
      const croppedDataUrl = canvas.toDataURL('image/png')
      croppedImageUrl.value = croppedDataUrl
      
      // 将裁剪后的图片转换为 File 对象
      canvas.toBlob((blob) => {
        const file = new File([blob], 'cropped-image.png', { type: 'image/png' })
        emit('cropped-image', file)
      }, 'image/png')
    }
    
    img.src = props.imageUrl
  } catch (error) {
    console.error('裁剪图片失败:', error)
  }
}

// 暴露方法
defineExpose({
  resetCrop,
  confirmCrop
})
</script>

<style scoped>
.image-cropper {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.cropper-container {
  position: relative;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}

.cropper-image {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: contain;
  display: block;
  cursor: crosshair;
  user-select: none;
}

.crop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.crop-area {
  position: relative;
  border: 2px solid #42b983;
  background: transparent;
}

.crop-handles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #42b983;
  border: 1px solid #fff;
  border-radius: 50%;
}

.handle-nw {
  top: -4px;
  left: -4px;
}

.handle-ne {
  top: -4px;
  right: -4px;
}

.handle-sw {
  bottom: -4px;
  left: -4px;
}

.handle-se {
  bottom: -4px;
  right: -4px;
}

.cropper-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #369870;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.cropped-preview {
  margin-top: 2rem;
  text-align: center;
}

.cropped-preview h4 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
}

.preview-image {
  max-width: 200px;
  max-height: 200px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
