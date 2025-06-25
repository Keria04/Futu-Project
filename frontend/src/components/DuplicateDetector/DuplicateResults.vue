<template>
  <div class="duplicate-results">
    <h3 class="results-title">重复图片组 ({{ groups.length }})</h3>
    
    <div class="groups-container">
      <div 
        v-for="(group, index) in groups" 
        :key="index"
        class="duplicate-group"
      >
        <div class="group-header">
          <h4 class="group-title">重复组 {{ index + 1 }}</h4>
          <span class="group-count">{{ group.length }} 张图片</span>
        </div>
        
        <div class="group-items">
          <div 
            v-for="imageId in group" 
            :key="imageId"
            class="group-item"
          >
            <div class="item-id">图片ID: {{ imageId }}</div>
            <!-- 这里可以扩展显示图片预览 -->
          </div>
        </div>
      </div>
    </div>
    
    <div class="results-summary">
      <p class="summary-text">
        共发现 <strong>{{ groups.length }}</strong> 组重复图片，
        涉及 <strong>{{ totalDuplicateImages }}</strong> 张图片
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  groups: {
    type: Array,
    required: true
  }
})

// 计算重复图片总数
const totalDuplicateImages = computed(() => {
  return props.groups.reduce((total, group) => total + group.length, 0)
})
</script>

<style scoped>
.duplicate-results {
  margin-top: 2rem;
}

.results-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.groups-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.duplicate-group {
  background: #fff5f5;
  border: 1px solid #ffcccb;
  border-radius: 8px;
  padding: 1rem;
  transition: box-shadow 0.2s ease;
}

.duplicate-group:hover {
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.1);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ffe0e0;
}

.group-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #d32f2f;
  margin: 0;
}

.group-count {
  font-size: 0.9rem;
  color: #666;
  background: #ffe0e0;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.group-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.group-item {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.5rem 0.8rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.group-item:hover {
  background: #f5f5f5;
  border-color: #d0d0d0;
}

.item-id {
  color: #555;
  font-weight: 500;
}

.results-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.summary-text {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.summary-text strong {
  color: #d32f2f;
  font-weight: 600;
}

@media (max-width: 768px) {
  .group-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .group-items {
    flex-direction: column;
  }
  
  .group-item {
    width: 100%;
  }
}
</style>
