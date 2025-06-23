<template>
  <div class="image-search">
    <h2 class="section-title">图片检索</h2>
    
    <DatasetManager
      :dataset-names="datasetNames"
      @add-dataset="addDataset"
      @remove-dataset="removeDataset"
    />

    <div class="upload-section">
      <input 
        class="file-input" 
        type="file" 
        accept="image/*" 
        @change="onFileChange"
        ref="fileInputRef"
      />
      
      <ImageCanvas
        ref="imageCanvasRef"
        :preview-url="previewUrl"
        :crop="crop"
        @mouse-down="handleMouseDown"
        @mouse-up="handleMouseUp"
      />
      
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
 * 执行图片搜索
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
  
  // 添加数据集名称
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
    message.value = '检索失败，请重试'
    messageType.value = 'error'
    console.error('Search error:', error)
  } finally {
    stopLoading()
  }
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

.file-input {
  padding: 0.5rem;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  transition: border-color 0.2s;
}

.file-input:hover {
  border-color: #42b983;
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
