<template>
  <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>图片框选</h3>
        <button class="close-btn" @click="closeModal">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="cropper-section">
          <div class="instructions">
            <p>在图片上拖拽鼠标来框选要搜索的区域</p>
          </div>
          
          <ImageCropper
            :image-url="imageUrl"
            @crop-change="onCropChange"
            ref="imageCropperRef"
          />
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">
          取消
        </button>
        <button class="btn btn-primary" @click="confirmSelection" :disabled="!hasCropArea || isConfirming">
          {{ isConfirming ? '处理中...' : '确认框选' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import ImageCropper from './ImageCropper.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  imageUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'confirm', 'crop-change', 'cropped-image'])

// 组件引用
const imageCropperRef = ref(null)

// 状态
const hasCropArea = ref(false)
const cropData = ref(null)
const isConfirming = ref(false)

// 监听visible变化，重置状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetState()
  }
})

function resetState() {
  hasCropArea.value = false
  cropData.value = null
  isConfirming.value = false
}

function onCropChange(data) {
  cropData.value = data
  hasCropArea.value = data.w > 0 && data.h > 0
  emit('crop-change', data)
}

function onCroppedImage(file) {
  // 这个方法现在不需要做任何事情，因为我们在confirmSelection中直接生成图片
}

function handleOverlayClick() {
  closeModal()
}

function closeModal() {
  emit('close')
}

async function confirmSelection() {
  if (!hasCropArea.value || !cropData.value || isConfirming.value) {
    return
  }
  
  isConfirming.value = true
  
  try {
    // 直接在这里生成裁剪图片，不依赖ImageCropper组件
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    canvas.width = cropData.value.w
    canvas.height = cropData.value.h
    
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    const cropPromise = new Promise((resolve, reject) => {
      img.onload = () => {
        try {
          ctx.drawImage(
            img,
            cropData.value.x,
            cropData.value.y,
            cropData.value.w,
            cropData.value.h,
            0,
            0,
            cropData.value.w,
            cropData.value.h
          )
          
          canvas.toBlob((blob) => {
            const file = new File([blob], 'cropped-image.png', { type: 'image/png' })
            resolve(file)
          }, 'image/png')
        } catch (error) {
          reject(error)
        }
      }
      
      img.onerror = () => {
        reject(new Error('图片加载失败'))
      }
      
      img.src = props.imageUrl
    })
    
    const croppedFile = await cropPromise
    
    // 直接发送确认事件
    emit('confirm', {
      cropData: cropData.value,
      croppedFile: croppedFile
    })
    
    closeModal()
  } catch (error) {
    console.error('确认框选失败:', error)
  } finally {
    isConfirming.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  resetCrop: () => {
    if (imageCropperRef.value) {
      imageCropperRef.value.resetCrop()
    }
    resetState()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 90vh;
  width: 800px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f8fafc;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.cropper-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.instructions {
  text-align: center;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #42b983;
}

.instructions p {
  margin: 0;
  color: #333;
  font-size: 0.95rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  background: #f8fafc;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
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
  transform: translateY(-1px);
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-container {
    width: 95vw;
    height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
