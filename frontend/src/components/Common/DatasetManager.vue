<template>
  <div class="dataset-manager">
    <div class="dataset-list">
      <div 
        v-for="(name, idx) in datasetNames" 
        :key="idx" 
        class="dataset-item"
      >
        <div style="display: flex; width: 100%; gap: 0.5rem; align-items: center;">
          <input
            class="dataset-input"
            type="text"
            v-model="datasetNames[idx]"
            :placeholder="`请输入数据集名称${datasetNames.length > 1 ? '（可多选）' : ''}`"
            style="flex: 1;"
          />
          <select v-if="allDatasets.length" v-model="datasetNames[idx]" class="dataset-select">
            <option value="" disabled>请选择</option>
            <option v-for="ds in allDatasets" :key="ds.id" :value="ds.id">{{ ds.id }}</option>
          </select>
        </div>
        <button 
          v-if="datasetNames.length > 1" 
          class="btn btn-remove" 
          @click="$emit('remove-dataset', idx)"
        >
          -
        </button>
      </div>
    </div>
    <button class="btn btn-add" @click="$emit('add-dataset')">
      + 添加数据集
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { datasetApi } from '@/services/api'

defineProps({
  datasetNames: {
    type: Array,
    required: true
  }
})

defineEmits(['add-dataset', 'remove-dataset'])

const allDatasets = ref([])

onMounted(async () => {
  try {
    const res = await datasetApi.getDatasets()
    allDatasets.value = res.data.datasets || []
  } catch (e) {
    allDatasets.value = []
  }
})
</script>

<style scoped>
.dataset-manager {
  width: 100%;
  margin-bottom: 1rem;
}

.dataset-list {
  margin-bottom: 0.5rem;
}

.dataset-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.3rem;
  gap: 0.5rem;
}

.dataset-input {
  flex: 1;
  padding: 0.4rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.dataset-input:focus {
  outline: none;
  border-color: #42b983;
}

.btn {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-add {
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  color: white;
  padding: 0.4rem 0.8rem;
}

.btn-add:hover {
  background: linear-gradient(90deg, #42b983 0%, #2d8cf0 100%);
}

.btn-remove {
  background: #ff6b6b;
  color: white;
  padding: 0.2rem 0.6rem;
  min-width: 30px;
}

.btn-remove:hover {
  background: #ff5252;
}

.dataset-select {
  min-width: 100px;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 1rem;
  margin-left: 0.3rem;
}
</style>
