<template>
  <div class="duplicate-results" :class="{ 'results-show': groups.length > 0 }">
    <h3 class="results-title">重复图片组 ({{ groups.length }})</h3>
    
    <div class="groups-container">
      <div 
        v-for="(group, index) in groups" 
        :key="`group-${animationKey}-${index}`"
        class="duplicate-group"
        :style="{ 'animation-delay': (index * 0.15) + 's' }"
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
import { ref, computed, watch } from 'vue'

const props = defineProps({
  groups: {
    type: Array,
    required: true
  }
})

// 动画触发键，用于强制重新触发动画
const animationKey = ref(0)

// 监听结果变化，触发动画重新播放
watch(() => props.groups, () => {
  animationKey.value++
}, { deep: true })

// 计算重复图片总数
const totalDuplicateImages = computed(() => {
  return props.groups.reduce((total, group) => total + group.length, 0)
})
</script>

<style scoped>
.duplicate-results {
  margin-top: 2rem;
  opacity: 0;
  transform: translateY(-30px);
  max-height: 0;
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.duplicate-results.results-show {
  opacity: 1;
  transform: translateY(0);
  max-height: none;
  overflow: visible;
}

.results-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
  opacity: 0;
  transform: translateX(-20px);
  animation: titleSlideIn 0.5s ease-out 0.2s forwards;
}

@keyframes titleSlideIn {
  0% {
    opacity: 0;
    transform: translateX(-20px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(40px) scale(0.95);
  animation: fadeInUpGroup 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes fadeInUpGroup {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  60% {
    opacity: 0.8;
    transform: translateY(-5px) scale(1.02);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.duplicate-group:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.2);
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
