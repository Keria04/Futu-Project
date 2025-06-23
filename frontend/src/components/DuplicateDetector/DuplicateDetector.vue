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
      </div>
      
      <button 
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
import { ref, computed } from 'vue'
import { duplicateApi, datasetApi } from '../../services/api.js'
import { useLoading } from '../../composables/useLoading.js'
import DatasetManager from '../Common/DatasetManager.vue'
import MessageDisplay from '../Common/MessageDisplay.vue'
import DuplicateResults from './DuplicateResults.vue'

// 状态管理
const { loading, message, startLoading, stopLoading } = useLoading()
const messageType = ref('info')

// 单个数据集名称（重复检测通常针对单个数据集）
const singleDataset = ref([''])
const threshold = ref(95)
const duplicateGroups = ref([])

/**
 * 查找重复图片
 */
async function findDuplicates() {
  const datasetName = singleDataset.value[0]?.trim()
  if (!datasetName) {
    message.value = '请填写数据集名称'
    messageType.value = 'warning'
    return
  }

  startLoading('正在查找重复图片...')
  duplicateGroups.value = []
  messageType.value = 'info'

  try {
    // 获取数据集ID
    const datasetResponse = await datasetApi.getDatasetId(datasetName)
    const datasetId = datasetResponse.data.id

    // 查找重复图片
    const duplicateResponse = await duplicateApi.findDuplicates(
      datasetId,
      threshold.value,
      false
    )

    duplicateGroups.value = duplicateResponse.data.groups || []
    
    if (duplicateGroups.value.length === 0) {
      message.value = '未检测到重复图片'
      messageType.value = 'info'
    } else {
      message.value = `找到 ${duplicateGroups.value.length} 组重复图片`
      messageType.value = 'success'
    }
  } catch (error) {
    message.value = '查重失败，请检查数据集名称是否正确'
    messageType.value = 'error'
    console.error('Duplicate detection error:', error)
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
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  align-self: flex-start;
}

.btn-detect {
  background: linear-gradient(90deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.btn-detect:hover:not(:disabled) {
  background: linear-gradient(90deg, #ee5a52 0%, #ff6b6b 100%);
  transform: translateY(-1px);
}

.btn:disabled {
  background: #ffb3b3;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
}

@media (max-width: 768px) {
  .detector-controls {
    align-items: stretch;
  }
  
  .threshold-control {
    justify-content: space-between;
  }
  
  .btn {
    align-self: stretch;
  }
}
</style>
