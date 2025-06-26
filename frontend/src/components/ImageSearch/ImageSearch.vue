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
      <ProgressBar :progress="searchProgress" :is-visible="showProgressBar" />
      <button 
        class="btn btn-search" 
        :disabled="!selectedFile || loading"
        @click="searchImage"
      >
        {{ loading ? '检索中...' : '上传并检索' }}
      </button>
    </div>
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
import { ref } from 'vue'
import { searchApi } from '../../services/api.js'
import { useImageHandler } from '../../composables/useImageHandler.js'
import { useDatasetManager } from '../../composables/useDatasetManager.js'
import { useLoading } from '../../composables/useLoading.js'
import DatasetManager from '../Common/DatasetManager.vue'
import ImageCanvas from '../Common/ImageCanvas.vue'
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

// 搜索结果
const results = ref([])
const selectedFile = ref(null)
const messageType = ref('info')
const searchProgress = ref(0)
const showProgressBar = ref(false)

/**
 * 处理文件选择
 */
function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  selectedFile.value = file
  handleFileChange(file)
  
  // 将 canvas ref 传递给 composable
  if (imageCanvasRef.value) {
    canvasRef.value = imageCanvasRef.value.canvasRef
  }
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

  startLoading('正在检索图片...')
  results.value = []
  messageType.value = 'info'
  
  const formData = new FormData()
  formData.append('query_img', selectedFile.value)
  formData.append('crop_x', crop.x)
  formData.append('crop_y', crop.y)
  formData.append('crop_w', crop.w)
  formData.append('crop_h', crop.h)
  validation.names.forEach(name => {
    formData.append('dataset_names[]', name)
  })

  try {
    const response = await searchApi.searchImage(formData)
    results.value = response.data.results || []
    if (results.value.length === 0) {
      message.value = '未找到相似图片'
      messageType.value = 'info'
    } else {
      message.value = `找到 ${results.value.length} 张相似图片`
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
</style>
