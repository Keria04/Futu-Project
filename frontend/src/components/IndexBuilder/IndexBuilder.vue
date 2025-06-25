<template>
  <div class="index-builder">
    <h2 class="section-title">索引构建</h2>
    
    <DatasetManager
      :dataset-names="datasetNames"
      @add-dataset="addDataset"
      @remove-dataset="removeDataset"
    />

    <div class="btn-group">
      <button 
        class="btn btn-primary" 
        :disabled="loading"
        @click="buildIndex(false)"
      >
        本地构建索引
      </button>
      <button 
        class="btn btn-primary" 
        :disabled="loading"
        @click="buildIndex(true)"
      >
        远程构建索引
      </button>
    </div>

    <MessageDisplay 
      v-if="message"
      :message="message"
      :type="messageType"
    />

    <ProgressBar
      :progress="buildProgress"
      :status="buildStatus"
      :is-visible="isProgressVisible"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { indexApi } from '../../services/api.js'
import { useDatasetManager } from '../../composables/useDatasetManager.js'
import { useLoading } from '../../composables/useLoading.js'
import { useProgress } from '../../composables/useLoading.js'
import DatasetManager from '../Common/DatasetManager.vue'
import MessageDisplay from '../Common/MessageDisplay.vue'
import ProgressBar from '../Common/ProgressBar.vue'

// 数据集管理
const { datasetNames, addDataset, removeDataset, validateDatasets } = useDatasetManager()

// 加载状态管理
const { loading, message, startLoading, stopLoading } = useLoading()

// 进度管理
const { 
  progress: buildProgress, 
  status: buildStatus, 
  isVisible: isProgressVisible,
  setProgress,
  resetProgress 
} = useProgress()

// 消息类型
const messageType = ref('info')

// 进度轮询定时器
let progressTimer = null

/**
 * 构建索引
 */
async function buildIndex(distributed = false) {
  const validation = validateDatasets()
  if (!validation.isValid) {
    message.value = validation.message
    messageType.value = 'warning'
    return
  }

  startLoading('正在构建索引...')
  resetProgress()
  messageType.value = 'info'

  try {
    const response = await indexApi.buildIndex(validation.names, distributed)
    message.value = response.data.msg
    messageType.value = 'success'

    // 开始轮询进度
    if (response.data.progress && response.data.progress.length > 0) {
      const progressUrl = response.data.progress[0].progress_file
      pollProgress(progressUrl)
    }
  } catch (error) {
    message.value = '构建索引失败'
    messageType.value = 'error'
    console.error('Build index error:', error)
  } finally {
    stopLoading()
  }
}

/**
 * 轮询构建进度
 */
function pollProgress(progressUrl) {
  if (progressTimer) {
    clearInterval(progressTimer)
  }

  progressTimer = setInterval(async () => {
    try {
      const response = await indexApi.getProgress(progressUrl)
      console.log('Progress response:', response.data) // 添加调试日志
      setProgress(response.data.progress, response.data.status)
      
      if (response.data.status === 'done') {
        clearInterval(progressTimer)
        progressTimer = null
        // 根据消息内容设置不同的提示
        if (response.data.message) {
          message.value = response.data.message
        } else {
          message.value = '索引构建完成'
        }
        messageType.value = 'success'
      } else if (response.data.status === 'error') {
        clearInterval(progressTimer)
        progressTimer = null
        message.value = '索引构建失败'
        messageType.value = 'error'
      }
    } catch (error) {
      console.warn('Progress polling error:', error)
      // 如果连续出错，停止轮询
      if (error.response && error.response.status >= 400) {
        clearInterval(progressTimer)
        progressTimer = null
        message.value = '获取构建进度失败'
        messageType.value = 'error'
      }
    }
  }, 1000)
}

// 组件销毁时清理定时器
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  if (progressTimer) {
    clearInterval(progressTimer)
  }
})
</script>

<style scoped>
.index-builder {
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

.btn-group {
  display: flex;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
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
