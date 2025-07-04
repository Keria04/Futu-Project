<template>
  <div class="image-search">
    <h2 class="section-title">图片检索</h2>
    <DatasetManager
      :dataset-names="datasetNames"
      @add-dataset="addDataset"
      @remove-dataset="removeDataset"
    />
    <div class="upload-section">
      <div class="custom-upload-box" @click="triggerFileInput">
        <input 
          class="file-input" 
          type="file" 
          accept="image/*" 
          @change="onFileChange"
          ref="fileInputRef"
        />
        <div v-if="!previewUrl" class="upload-content">
          <svg width="48" height="48" viewBox="0 0 1024 1024" fill="none"><path d="M512 128v512m0 0l-192-192m192 192l192-192" stroke="#b5b5b5" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/><rect x="128" y="704" width="768" height="192" rx="48" fill="#f5f6fa" stroke="#e0e0e0" stroke-width="4"/></svg>
          <div class="upload-text">
            <span>在此处上传您的图片，或 <span class="upload-link">浏览</span></span>
            <div class="upload-tip">最大文件大小：20MB</div>
          </div>
        </div>
        <div v-else class="preview-img-wrapper">
          <img :src="previewUrl" class="preview-img-full" />
        </div>
      </div>
      
      <!-- 框选功能按钮区域 -->
      <div v-if="previewUrl" class="crop-button-section">
        <div class="crop-status">
          <div v-if="!hasCroppedImage" class="status-item">
            <span class="status-icon">📷</span>
            <span class="status-text">当前将搜索整张图片</span>
          </div>
          <div v-else class="status-item success">
            <span class="status-icon">✅</span>
            <span class="status-text">已框选区域，将搜索框选部分</span>
          </div>
        </div>
        
        <div class="crop-actions">
          <button 
            class="btn btn-crop" 
            @click="openCropModal"
            :disabled="loading"
          >
            {{ hasCroppedImage ? '重新框选区域' : '框选搜索区域' }}
          </button>
          <button 
            v-if="hasCroppedImage"
            class="btn btn-reset" 
            @click="resetCrop"
            :disabled="loading"
          >
            清除框选
          </button>
        </div>
        
        <!-- 框选结果预览 -->
        <div v-if="hasCroppedImage && croppedImagePreview" class="crop-preview">
          <h4>框选区域预览</h4>
          <img :src="croppedImagePreview" class="preview-cropped-image" />
        </div>
      </div>
      
      <ProgressBar :progress="searchProgress" :is-visible="showProgressBar" />
      
      <!-- 检索数量选择 -->
      <div class="search-config">
        <div class="config-item">
          <label for="topK" class="config-label">检索数量：</label>
          <input 
            id="topK"
            v-model.number="topK" 
            type="number" 
            min="1" 
            max="128"
            class="config-input"
            :class="{ 'error': topKError }"
            @input="validateTopK"
            placeholder="输入1-128之间的数字"
          />
          <span class="config-unit">张</span>
        </div>
        <div v-if="topKError" class="error-message">
          {{ topKErrorMessage }}
        </div>
        <div class="config-hint">
          建议检索数量不超过50张以获得更好的性能
        </div>
      </div>
      
      <div class="search-buttons">
        <button 
          class="btn btn-search" 
          :disabled="!selectedFile || loading"
          @click="searchImage"
        >
          {{ loading ? '检索中...' : (hasCroppedImage ? '搜索框选区域' : '搜索整张图片') }}
        </button>
      </div>
    </div>
    
    <!-- 框选弹窗 -->
    <CropperModal
      :visible="showCropModal"
      :image-url="previewUrl"
      @close="closeCropModal"
      @confirm="onCropConfirm"
      ref="cropperModalRef"
    />
    
    <MessageDisplay 
      v-if="message"
      :message="message"
      :type="messageType"
    />
    <SearchResults
      v-if="results.length > 0"
      :results="results"
    />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { searchApi } from '../../services/api.js'
import { useImageHandler } from '../../composables/useImageHandler.js'
import { useDatasetManager } from '../../composables/useDatasetManager.js'
import { useLoading } from '../../composables/useLoading.js'
import DatasetManager from '../Common/DatasetManager.vue'
import ImageCanvas from '../Common/ImageCanvas.vue'
import ImageCropper from '../Common/ImageCropper.vue'
import CropperModal from '../Common/CropperModal.vue'
import MessageDisplay from '../Common/MessageDisplay.vue'
import SearchResults from './SearchResults.vue'
import ProgressBar from '../Common/ProgressBar.vue'

// 图片处理
const {
  previewUrl,
  canvasRef,
  crop,
  handleFileChange,
  onMouseDown,
  onMouseUp
} = useImageHandler()

// 数据集管理
const { datasetNames, addDataset, removeDataset, validateDatasets } = useDatasetManager()

// 加载状态
const { loading, message, startLoading, stopLoading } = useLoading()

// 组件引用
const fileInputRef = ref(null)
const imageCanvasRef = ref(null)
const imageCropperRef = ref(null)
const cropperModalRef = ref(null)

// 搜索结果
const results = ref([])
const selectedFile = ref(null)
const messageType = ref('info')
const searchProgress = ref(0)
const showProgressBar = ref(false)

// 检索数量配置
const topK = ref(10)
const topKError = ref(false)
const topKErrorMessage = ref('')

// 框选相关状态
const hasCroppedImage = ref(false)
const croppedImageFile = ref(null)
const croppedImagePreview = ref('')
const cropArea = ref({ x: 0, y: 0, w: 0, h: 0 })
const showCropModal = ref(false)

/**
 * 验证检索数量
 */
function validateTopK() {
  const value = topK.value
  topKError.value = false
  topKErrorMessage.value = ''
  
  if (!value || value < 1) {
    topKError.value = true
    topKErrorMessage.value = '检索数量必须大于0'
    return false
  }
  
  if (value > 128) {
    topKError.value = true
    topKErrorMessage.value = '检索数量不能超过128张，请重新输入'
    return false
  }
  
  return true
}

/**
 * 处理文件选择
 */
function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  selectedFile.value = file
  handleFileChange(file)
  
  // 重置框选状态
  resetCropState()
  
  // 将 canvas ref 传递给 composable
  if (imageCanvasRef.value) {
    canvasRef.value = imageCanvasRef.value.canvasRef
  }
}

/**
 * 处理框选区域变化
 */
function onCropChange(cropData) {
  cropArea.value = cropData
  crop.x = cropData.x
  crop.y = cropData.y
  crop.w = cropData.w
  crop.h = cropData.h
}

/**
 * 打开框选弹窗
 */
function openCropModal() {
  showCropModal.value = true
}

/**
 * 关闭框选弹窗
 */
function closeCropModal() {
  showCropModal.value = false
}

/**
 * 确认框选结果
 */
function onCropConfirm(data) {
  hasCroppedImage.value = true
  cropArea.value = data.cropData
  croppedImageFile.value = data.croppedFile
  
  // 创建预览URL
  if (data.croppedFile) {
    croppedImagePreview.value = URL.createObjectURL(data.croppedFile)
  }
  
  message.value = '已框选区域，将使用框选后的图片进行搜索'
  messageType.value = 'success'
  
  showCropModal.value = false
}

/**
 * 重置框选状态
 */
function resetCropState() {
  hasCroppedImage.value = false
  croppedImageFile.value = null
  croppedImagePreview.value = ''
  cropArea.value = { x: 0, y: 0, w: 0, h: 0 }
  
  // 清理预览URL
  if (croppedImagePreview.value && croppedImagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(croppedImagePreview.value)
  }
}

/**
 * 重置框选
 */
function resetCrop() {
  resetCropState()
  if (cropperModalRef.value) {
    cropperModalRef.value.resetCrop()
  }
  message.value = '已重置框选，将搜索整张图片'
  messageType.value = 'info'
}

/**
 * 处理鼠标按下
 */
function handleMouseDown(event) {
  if (imageCanvasRef.value) {
    canvasRef.value = imageCanvasRef.value.canvasRef
  }
  onMouseDown(event)
}

/**
 * 处理鼠标抬起
 */
function handleMouseUp(event) {
  onMouseUp(event)
}

/**
 * 执行图片检索（直接查询，不构建索引）
 */
async function searchImage() {
  const validation = validateDatasets()
  if (!validation.isValid) {
    message.value = validation.message
    messageType.value = 'warning'
    return
  }
  if (!selectedFile.value) {
    message.value = '请选择要检索的图片'
    messageType.value = 'warning'
    return
  }
  
  // 验证检索数量
  if (!validateTopK()) {
    messageType.value = 'warning'
    return
  }

  startLoading(hasCroppedImage.value ? '正在检索框选区域...' : '正在检索图片...')
  
  // 清空之前的结果，确保动画能够正确触发
  results.value = []
  
  messageType.value = 'info'
  
  const formData = new FormData()
  
  // 如果有框选的图片，使用框选后的图片，否则使用原图片
  if (hasCroppedImage.value && croppedImageFile.value) {
    formData.append('query_img', croppedImageFile.value)
    // 框选后的图片不需要再传递裁剪坐标
    formData.append('crop_x', 0)
    formData.append('crop_y', 0)
    formData.append('crop_w', 0)
    formData.append('crop_h', 0)
  } else {
    formData.append('query_img', selectedFile.value)
    formData.append('crop_x', crop.x)
    formData.append('crop_y', crop.y)
    formData.append('crop_w', crop.w)
    formData.append('crop_h', crop.h)
  }
  
  validation.names.forEach(name => {
    formData.append('dataset_names[]', name)
  })
  
  // 添加检索数量参数
  formData.append('top_k', topK.value)
  
  // 添加检索数量
  formData.append('top_k', topK.value)

  try {
    const response = await searchApi.searchImage(formData)
    
    // 使用 nextTick 确保 DOM 更新后再设置结果，以触发动画
    await nextTick()
    results.value = response.data.results || []
    
    if (results.value.length === 0) {
      message.value = '未找到相似图片'
      messageType.value = 'info'
    } else {
      const searchType = hasCroppedImage.value ? '框选区域' : '图片'
      message.value = `在${searchType}中找到 ${results.value.length} 张相似图片`
      messageType.value = 'success'
    }
  } catch (error) {
    // 如果是索引不存在的错误，给出友好提示
    if (error.response && error.response.data && error.response.data.error) {
      const errorMsg = error.response.data.error
      if (errorMsg.includes('index') || errorMsg.includes('索引')) {
        message.value = '请先在数据集管理页面上传图片以构建索引'
        messageType.value = 'warning'
      } else {
        message.value = errorMsg
        messageType.value = 'error'
      }
    } else {
      message.value = '检索失败，请重试'
      messageType.value = 'error'
    }
    console.error('Search error:', error)
  } finally {
    stopLoading()
  }
}

/**
 * 触发文件输入框点击
 */
function triggerFileInput() {
  fileInputRef.value && fileInputRef.value.click()
}
</script>

<style scoped>
.image-search {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.4rem;
  color: #333;
  margin-bottom: 1rem;
  font-weight: 600;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.custom-upload-box {
  width: 100%;
  min-height: 180px;
  background: #f8fafc;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  cursor: pointer;
  position: relative;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}

.custom-upload-box:hover {
  border-color: #42b983;
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.upload-text {
  color: #888;
  font-size: 1.1rem;
  margin-top: 0.5rem;
  text-align: center;
}

.upload-link {
  color: #42b983;
  text-decoration: underline;
  cursor: pointer;
}

.upload-tip {
  color: #bbb;
  font-size: 0.95rem;
  margin-top: 0.2rem;
}

.preview-img-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-img-full {
  display: block;
  max-width: 100%;
  max-height: 320px;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  object-fit: contain;
  background: #fff;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-search {
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  color: white;
  min-width: 160px;
}

.btn-search:hover:not(:disabled) {
  background: linear-gradient(90deg, #42b983 0%, #2d8cf0 100%);
  transform: translateY(-1px);
}

.btn:disabled {
  background: #b5e2d4;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

/* 新增的框选按钮区域样式 */
.crop-button-section {
  width: 100%;
  margin: 1.5rem 0;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.crop-status {
  margin-bottom: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.status-item.success {
  background: #f0f9ff;
  border-color: #42b983;
}

.status-icon {
  font-size: 1.2rem;
}

.status-text {
  color: #555;
  font-size: 0.95rem;
  font-weight: 500;
}

.status-item.success .status-text {
  color: #42b983;
}

.crop-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.btn-crop {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-crop:hover:not(:disabled) {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.crop-preview {
  margin-top: 1rem;
  text-align: center;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.crop-preview h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.preview-cropped-image {
  max-width: 150px;
  max-height: 150px;
  border: 2px solid #42b983;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.2);
}

/* 检索配置样式 */
.search-config {
  width: 100%;
  margin: 1rem 0;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.config-label {
  font-size: 0.9rem;
  color: #555;
  font-weight: 500;
  min-width: 80px;
}

.config-input {
  padding: 0.4rem 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  width: 120px;
  transition: border-color 0.2s;
}

.config-input:focus {
  outline: none;
  border-color: #42b983;
}

.config-input.error {
  border-color: #e74c3c;
  background-color: #fdf2f2;
}

.config-unit {
  font-size: 0.9rem;
  color: #666;
}

.config-hint {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.5rem;
}

.error-message {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.2rem;
}

@media (max-width: 768px) {
  .crop-button-section {
    padding: 1rem;
    margin: 1rem 0;
  }
  
  .crop-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn-crop {
    width: 100%;
  }
  
  .search-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>
