<template>
  <div class="search-results">
    <h3 class="results-title">检索结果 ({{ results.length }})</h3>
    
    <div class="results-grid">
      <div 
        v-for="(item, index) in results" 
        :key="`${item.idx}-${item.dataset}-${index}`"
        class="result-item"
      >        <div class="result-image">
          <img 
            :src="fixImageUrl(item.img_url || item.image_path)" 
            :alt="item.fname"
            @error="handleImageError"
          />
        </div>
        
        <div class="result-info">
          <div class="result-filename">{{ item.fname }}</div>
          
          <div class="result-meta">
            <span class="result-id">编号: {{ item.idx }}</span>
            <span v-if="item.dataset" class="result-dataset">
              [{{ item.dataset }}]
            </span>
          </div>
          
          <div v-if="item.similarity !== undefined" class="result-similarity">
            相似度: {{ item.similarity.toFixed(2) }}%
          </div>
          
          <div 
            v-if="item.description && Object.keys(item.description).length" 
            class="result-description"
          >
            <div 
              v-for="(val, key) in item.description" 
              :key="key" 
              class="desc-item"
            >
              <strong>{{ key }}:</strong> {{ val }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  results: {
    type: Array,
    required: true
  }
})

/**
 * 修正图片URL
 */
function fixImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  // 自动补全为后端端口
  return `http://localhost:19198${url}`
}

function handleImageError(event) {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPgogIDx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjEyIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5Yqg6L295aSx6LSlPC90ZXh0Pgo8L3N2Zz4K'
}
</script>

<style scoped>
.search-results {
  margin-top: 2rem;
}

.results-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
  font-weight: 600;
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
  transition: all 0.2s ease;
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
  margin-bottom: 0.5rem;
  word-break: break-all;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.result-id {
  color: #666;
}

.result-dataset {
  color: #42b983;
  font-weight: 500;
}

.result-similarity {
  color: #2d8cf0;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.result-description {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e9ecef;
}

.desc-item {
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
  color: #555;
}

.desc-item strong {
  color: #333;
}

@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .result-image {
    height: 150px;
  }
}
</style>
