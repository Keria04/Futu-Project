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
          <span class="group-count">{{ group.images?.length || group.image_ids?.length || 0 }} 张图片</span>
        </div>
        
        <div class="group-items">
          <!-- 如果有图片信息，显示图片 -->
          <div 
            v-if="group.images && group.images.length > 0"
            v-for="image in group.images" 
            :key="image.id"
            class="group-item image-item"
          >
            <div class="image-preview">
              <img 
                :src="getImageUrl(image.image_url)" 
                :alt="`图片 ${image.id}`"
                @error="handleImageError"
                class="preview-img"
              />
            </div>
            <div class="image-info">
              <div class="item-id">ID: {{ image.id }}</div>
              <div class="item-dataset">数据集: {{ image.dataset_name }}</div>
              <div class="item-filename">文件: {{ image.filename }}</div>
            </div>
          </div>
          
          <!-- 如果只有ID，显示ID -->
          <div 
            v-else
            v-for="imageId in (group.image_ids || group)" 
            :key="imageId"
            class="group-item"
          >
            <div class="item-id">图片ID: {{ imageId }}</div>
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
  return props.groups.reduce((total, group) => {
    // 支持新旧两种数据格式
    if (group.images && group.images.length > 0) {
      return total + group.images.length
    } else if (group.image_ids && group.image_ids.length > 0) {
      return total + group.image_ids.length
    } else if (Array.isArray(group)) {
      return total + group.length
    }
    return total
  }, 0)
})

// 获取图片URL，处理相对路径
function getImageUrl(imageUrl) {
  if (!imageUrl) return ''
  // 如果是相对路径，添加后端基础URL
  if (imageUrl.startsWith('/')) {
    return `http://localhost:19198${imageUrl}`
  }
  return imageUrl
}

// 图片加载错误处理
function handleImageError(event) {
  console.error('图片加载失败:', event.target.src)
  event.target.style.display = 'none'
}
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.group-item {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.group-item:hover {
  background: #f5f5f5;
  border-color: #d0d0d0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-item {
  text-align: center;
}

.image-preview {
  margin-bottom: 0.5rem;
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 6px;
  overflow: hidden;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  border-radius: 4px;
  transition: transform 0.2s ease;
}

.preview-img:hover {
  transform: scale(1.05);
}

.image-info {
  width: 100%;
  font-size: 0.8rem;
  line-height: 1.3;
}

.item-id {
  color: #333;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.item-dataset {
  color: #666;
  margin-bottom: 0.2rem;
}

.item-filename {
  color: #888;
  font-size: 0.75rem;
  word-break: break-all;
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
