<template>
  <div class="duplicate-detector">
    <h2 class="section-title">查找重复图片</h2>
    <div class="detector-controls">
      <DatasetManager
        :dataset-names="singleDataset"
        @add-dataset="() => {}"
        @remove-dataset="() => {}"
      />
      <div class="threshold-control">
        <label for="threshold">相似度阈值:</label>
        <input 
          id="threshold"
          type="number" 
          v-model="threshold" 
          min="80" 
          max="100" 
          step="1"
          class="threshold-input"
        />
        <span class="threshold-unit">%</span>
      </div>      <button 
        class="btn btn-detect" 
        :disabled="loading"
        @click="findDuplicates"
      >
        {{ loading ? '查重中...' : '查找重复图片' }}
      </button>
    </div>
    <MessageDisplay 
      v-if="message"
      :message="message"
      :type="messageType"
    />
    <DuplicateResults
      v-if="duplicateGroups.length > 0"
      :groups="duplicateGroups"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { duplicateApi } from '../../services/api.js'
import { useLoading } from '../../composables/useLoading.js'
import DatasetManager from '../Common/DatasetManager.vue'
import MessageDisplay from '../Common/MessageDisplay.vue'
import DuplicateResults from './DuplicateResults.vue'

const { loading, message, startLoading, stopLoading } = useLoading()
const messageType = ref('info')
const singleDataset = ref([''])
const threshold = ref(95)
const duplicateGroups = ref([])

// 直接进行重复图片查找，不构建索引
async function findDuplicates() {
  const datasetName = singleDataset.value[0]?.trim()
  if (!datasetName) {
    message.value = '请填写数据集名称'
    messageType.value = 'warning'
    return
  }
    startLoading('正在查重...')
  duplicateGroups.value = []
  messageType.value = 'info'
  
  try {
    // 使用新的API获取带图片信息的重复组
    const resp = await duplicateApi.getDuplicateGroupsWithImages(datasetName, threshold.value)
    duplicateGroups.value = resp.data.groups || []
    if (duplicateGroups.value.length === 0) {
      message.value = '未找到重复图片'
      messageType.value = 'info'
    } else {
      message.value = `找到 ${duplicateGroups.value.length} 组重复图片`
      messageType.value = 'success'
    }
  } catch (error) {
    if (error.response && error.response.status === 500) {
      message.value = '索引文件不存在，请先构建索引'
      messageType.value = 'error'
    } else {
      message.value = '查重失败，请重试'
      messageType.value = 'error'
    }
    console.error('Duplicate error:', error)
  } finally {
    stopLoading()
  }
}


</script>

<style scoped>
.duplicate-detector {
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

.detector-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.threshold-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.threshold-control label {
  font-weight: 500;
  color: #555;
}

.threshold-input {
  width: 80px;
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  text-align: center;
}

.threshold-input:focus {
  outline: none;
  border-color: #42b983;
}

.threshold-unit {
  color: #666;
  font-size: 0.9rem;
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

.btn-detect {
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  color: white;
  min-width: 160px;
}

.btn-detect:hover:not(:disabled) {
  background: linear-gradient(90deg, #42b983 0%, #2d8cf0 100%);
  transform: translateY(-1px);
}

.btn:disabled {
  background: #b5e2d4;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
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
</style>
