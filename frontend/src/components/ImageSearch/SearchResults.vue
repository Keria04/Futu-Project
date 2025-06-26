<template>
  <div class="search-results" :class="{ 'results-show': results.length > 0 }">
    <h3 class="results-title">检索结果 ({{ results.length }})</h3>
    
    <div class="results-grid">
      <div 
        v-for="(item, index) in results" 
        :key="`${item.idx}-${item.dataset}-${index}`"
        class="result-item"
        :style="{ 'animation-delay': (index * 0.1) + 's' }"
      >
        <div class="result-image" @click="openImageModal(item)">
          <img 
            :src="item.img_url" 
            :alt="item.fname"
            @error="handleImageError"
          />
        </div>
        
        <div class="result-info">
          <div class="result-filename">{{ item.fname }}</div>
          
          <!-- 相似度信息 - 优先显示 -->
          <div v-if="item.similarity !== undefined" class="result-similarity">
            <div class="similarity-header">
              <span class="similarity-label">相似度</span>
              <span class="similarity-value">{{ item.similarity.toFixed(1) }}%</span>
            </div>
            <div class="similarity-progress">
              <div 
                class="similarity-progress-bar" 
                :style="{ 
                  '--progress-width': item.similarity + '%',
                  width: item.similarity + '%'
                }"
                :key="`similarity-${animationKey}-${item.idx}-${index}`"
              ></div>
            </div>
          </div>
          
          <!-- 基础信息 -->
          <div class="result-meta">
            <div class="meta-item">
              <span class="meta-label">编号:</span>
              <span class="meta-value">{{ item.idx }}</span>
            </div>
            <div v-if="item.dataset && item.dataset.trim()" class="meta-item">
              <span class="meta-label">数据集:</span>
              <span class="meta-value dataset-tag">{{ item.dataset }}</span>
            </div>
          </div>
          
          <!-- 详细描述信息 -->
          <div 
            v-if="hasValidDescription(item.description)" 
            class="result-description"
          >
            <div v-if="item.description.type && item.description.type.trim()" class="desc-item type-item">
              <span class="desc-label">类型:</span>
              <span class="desc-value">{{ item.description.type }}</span>
            </div>
            <div v-if="item.description.desc && item.description.desc.trim()" class="desc-item desc-item-main">
              <span class="desc-label">描述:</span>
              <span class="desc-value">{{ item.description.desc }}</span>
            </div>
            <!-- 其他动态字段 -->
            <div 
              v-for="(val, key) in getOtherFields(item.description)" 
              :key="key" 
              class="desc-item"
            >
              <span class="desc-label">{{ formatFieldName(key) }}:</span>
              <span class="desc-value">{{ val }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片放大模态框 - 使用 Teleport 渲染到 body -->
    <Teleport to="body">
      <div 
        v-if="selectedImage" 
        class="image-modal" 
        @click="closeImageModal"
      >
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="closeImageModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
          <img 
            :src="selectedImage.img_url" 
            :alt="selectedImage.fname"
            class="modal-image"
            @error="handleImageError"
          />
          <div class="modal-info">
            <h4 class="modal-title">{{ selectedImage.fname }}</h4>
            <div v-if="selectedImage.similarity !== undefined" class="modal-similarity">
              相似度: {{ selectedImage.similarity.toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  results: {
    type: Array,
    required: true
  }
})

// 动画触发键，用于强制重新触发动画
const animationKey = ref(0)

// 选中的图片信息
const selectedImage = ref(null)

// 打开图片模态框
function openImageModal(item) {
  selectedImage.value = item
  
  // 记录当前滚动位置
  const scrollY = window.scrollY
  
  // 完全锁定页面滚动
  document.body.style.overflow = 'hidden'
  document.documentElement.style.overflow = 'hidden'
  document.body.style.position = 'fixed'
  document.body.style.top = `-${scrollY}px`
  document.body.style.width = '100%'
  document.body.style.height = '100%'
  
  // 存储滚动位置以便恢复
  document.body.setAttribute('data-scroll-y', scrollY.toString())
}

// 关闭图片模态框
function closeImageModal() {
  // 获取之前的滚动位置
  const scrollY = document.body.getAttribute('data-scroll-y') || '0'
  
  selectedImage.value = null
  
  // 恢复页面滚动和位置
  document.body.style.overflow = ''
  document.documentElement.style.overflow = ''
  document.body.style.position = ''
  document.body.style.top = ''
  document.body.style.width = ''
  document.body.style.height = ''
  
  // 恢复滚动位置
  window.scrollTo(0, parseInt(scrollY))
  
  // 清理数据属性
  document.body.removeAttribute('data-scroll-y')
}

// ESC键关闭模态框
function handleEscKey(event) {
  if (event.key === 'Escape' && selectedImage.value) {
    closeImageModal()
  }
}

// 组件挂载时添加键盘事件监听
onMounted(() => {
  document.addEventListener('keydown', handleEscKey)
})

// 组件卸载时移除键盘事件监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
  
  // 确保页面滚动恢复正常
  const scrollY = document.body.getAttribute('data-scroll-y') || '0'
  document.body.style.overflow = ''
  document.documentElement.style.overflow = ''
  document.body.style.position = ''
  document.body.style.top = ''
  document.body.style.width = ''
  document.body.style.height = ''
  
  // 如果有保存的滚动位置，恢复它
  if (scrollY !== '0') {
    window.scrollTo(0, parseInt(scrollY))
  }
  
  document.body.removeAttribute('data-scroll-y')
})

// 监听结果变化，触发动画重新播放
watch(() => props.results, () => {
  animationKey.value++
}, { deep: true })

// 检查描述信息是否有有效内容
function hasValidDescription(description) {
  if (!description || typeof description !== 'object') {
    return false
  }
  
  // 检查是否有非空字符串值
  return Object.values(description).some(value => 
    value && typeof value === 'string' && value.trim().length > 0
  )
}

// 获取除了 type 和 desc 之外的其他字段
function getOtherFields(description) {
  if (!description || typeof description !== 'object') {
    return {}
  }
  
  const { type, desc, ...others } = description
  
  // 只返回有效的非空字段
  const validOthers = {}
  for (const [key, value] of Object.entries(others)) {
    if (value && typeof value === 'string' && value.trim()) {
      validOthers[key] = value
    }
  }
  
  return validOthers
}

// 格式化字段名称显示
function formatFieldName(fieldKey) {
  const fieldNameMap = {
    'size': '尺寸',
    'format': '格式',
    'category': '分类',
    'tags': '标签',
    'date': '日期',
    'author': '作者',
    'source': '来源'
  }
  
  return fieldNameMap[fieldKey] || fieldKey
}

function handleImageError(event) {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPgogIDx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjEyIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5Yqg6L295aSx6LSlPC90ZXh0Pgo8L3N2Zz4K'
}
</script>

<style scoped>
.search-results {
  margin-top: 2rem;
  opacity: 0;
  transform: translateY(-30px);
  max-height: 0;
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-results.results-show {
  opacity: 1;
  transform: translateY(0);
  max-height: none;
  overflow: visible;
}

.results-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
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

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.result-item {
  background: #f8fafb;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #e1e8ed;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(40px) scale(0.9);
  animation: fadeInUpBounce 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes fadeInUpBounce {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.9);
  }
  60% {
    opacity: 0.8;
    transform: translateY(-5px) scale(1.05);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.result-image {
  width: 100%;
  height: 200px;
  margin-bottom: 1rem;
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.result-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.result-info {
  text-align: left;
}

.result-filename {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.75rem;
  word-break: break-all;
  line-height: 1.3;
}

.result-similarity {
  margin-bottom: 0.75rem;
  padding: 0.8rem;
  background: #f8fbff;
  border: 1px solid #e3f2fd;
  border-radius: 12px;
  font-size: 0.9rem;
}

.similarity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.similarity-label {
  color: #2196f3;
  font-weight: 600;
  font-size: 0.85rem;
}

.similarity-value {
  color: #1976d2;
  font-weight: 700;
  font-size: 0.95rem;
}

.similarity-progress {
  width: 100%;
  height: 8px;
  background: #e3f2fd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.similarity-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4fc3f7 0%, #29b6f6 50%, #03a9f4 100%);
  border-radius: 4px;
  width: 0%;
  transition: width 2s cubic-bezier(0.4, 0, 0.2, 1);
  animation: progressSlide 2s cubic-bezier(0.4, 0, 0.2, 1) 0.5s forwards;
  position: relative;
  box-shadow: 0 2px 8px rgba(3, 169, 244, 0.3);
}

.similarity-progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);
  animation: shimmer 2.5s infinite 1s;
  border-radius: 4px;
}

@keyframes progressSlide {
  0% {
    width: 0%;
    transform: scaleX(0);
  }
  100% {
    width: var(--progress-width, 0%);
    transform: scaleX(1);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateX(100%);
    opacity: 0;
  }
}

.result-meta {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.meta-label {
  color: #666;
  font-weight: 500;
  min-width: fit-content;
}

.meta-value {
  color: #333;
  font-weight: 600;
}

.dataset-tag {
  background: #e8f5e8;
  color: #42b883;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.result-description {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e9ecef;
}

.desc-item {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.85rem;
  line-height: 1.4;
}

.desc-item:last-child {
  margin-bottom: 0;
}

.desc-label {
  color: #666;
  font-weight: 600;
  min-width: fit-content;
  font-size: 0.8rem;
}

.desc-value {
  color: #444;
  flex: 1;
}

.type-item .desc-value {
  background: #f0f8ff;
  color: #2d8cf0;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.desc-item-main .desc-value {
  font-style: italic;
  color: #555;
}

@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .result-image {
    height: 150px;
  }
}

/* 图片模态框样式 - 覆盖整个浏览器页面 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: modalFadeIn 0.4s ease-out;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  animation: modalSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 44px;
  height: 44px;
  background: rgba(0, 0, 0, 0.7);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  z-index: 10001;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.1);
}

.modal-image {
  display: block;
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.modal-info {
  padding: 20px;
  background: white;
  border-top: 1px solid #eee;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  word-break: break-all;
}

.modal-similarity {
  color: #2196f3;
  font-weight: 600;
  font-size: 0.95rem;
}

@keyframes modalFadeIn {
  0% {
    opacity: 0;
    background: rgba(0, 0, 0, 0);
    backdrop-filter: blur(0px);
    -webkit-backdrop-filter: blur(0px);
  }
  100% {
    opacity: 1;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
  }
}

@keyframes modalSlideIn {
  0% {
    transform: scale(0.7) translateY(-50px);
    opacity: 0;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .modal-content {
    max-width: 95vw;
    max-height: 95vh;
  }
  
  .modal-image {
    max-height: 70vh;
  }
  
  .modal-info {
    padding: 16px;
  }
  
  .modal-close {
    width: 36px;
    height: 36px;
    top: 12px;
    right: 12px;
  }
}
</style>
