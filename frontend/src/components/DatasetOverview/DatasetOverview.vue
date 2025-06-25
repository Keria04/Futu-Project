<template>
  <div class="dataset-overview">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">数据集管理</h2>
      <p class="page-description">管理和查看所有可用的图片数据集</p>
    </div>

    <!-- 数据集展示区域 -->
    <div class="datasets-section">
      <div class="datasets-container">
        <div 
          v-for="(dataset, idx) in datasets" 
          :key="dataset.id" 
          class="dataset-card"
          @click="selectDataset(dataset)"
          :class="{ active: selectedDatasets.includes(dataset.id) }"
        >
          <!-- 数据集头部 -->
          <div class="dataset-header">
            <div class="dataset-avatar">
              {{ idx + 1 }}
            </div>
            <div class="dataset-info">
              <h3 class="dataset-title">{{ dataset.name }}</h3>
              <p class="dataset-subtitle">数据集 {{ dataset.id }}</p>
            </div>
            <div class="dataset-menu">
              <button class="menu-button" @click.stop="toggleMenu(dataset.id)">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="2"></circle>
                  <circle cx="12" cy="5" r="2"></circle>
                  <circle cx="12" cy="19" r="2"></circle>
                </svg>
              </button>
            </div>
          </div>

          <!-- 数据集预览图 -->
          <div class="dataset-preview">
            <template v-if="dataset.first_image_url">
              <img :src="fixImageUrl(dataset.first_image_url)" alt="预览图" class="dataset-preview-img" @error="onImgError($event)" />
            </template>
            <template v-else>
              <div class="preview-placeholder">
                <!-- 简单的几何图形作为预览 -->
                <div class="preview-shapes">
                  <div class="shape triangle"></div>
                  <div class="shape square"></div>
                  <div class="shape circle"></div>
                </div>
              </div>
            </template>
          </div>

          <!-- 数据集描述 -->
          <div class="dataset-content">
            <h4 class="content-title">Title</h4>
            <p class="content-subtitle">Subhead</p>
            <p class="content-description">{{ dataset.description }}</p>
          </div>

          <!-- 操作按钮 -->
          <div class="dataset-actions">
            <input
              type="file"
              multiple
              :id="'upload-' + dataset.id"
              style="display:none"
              @change="e => handleUpload(e, dataset)"
            />
            <button 
              class="action-button primary"
              @click.stop="() => triggerUpload(dataset)"
            >
              上传图片
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { datasetApi } from '@/services/api'

// 响应式数据
const datasets = ref([])
const loading = ref(false)
const selectedDatasets = ref([])

// 获取数据集列表
const fetchDatasets = async () => {
  try {
    loading.value = true
    const response = await datasetApi.getDatasets()
    datasets.value = response.data.datasets.map(dataset => ({
      ...dataset,
      enabled: false
    }))
  } catch (error) {
    console.error('获取数据集失败:', error)
  } finally {
    loading.value = false
  }
}

// 选择数据集
const selectDataset = (dataset) => {
  const index = selectedDatasets.value.indexOf(dataset.id)
  if (index > -1) {
    selectedDatasets.value.splice(index, 1)
  } else {
    selectedDatasets.value.push(dataset.id)
  }
}

// 启用数据集
const enableDataset = (dataset) => {
  dataset.enabled = !dataset.enabled
  console.log('数据集状态切换:', dataset.name, dataset.enabled)
}

// 切换菜单
const toggleMenu = (datasetId) => {
  console.log('切换菜单:', datasetId)
}

// 修正图片URL（兼容端口、绝对路径等问题）
function fixImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  // 自动补全为后端端口
  return `http://localhost:19198${url}`
}
// 图片加载失败时回退为占位图
function onImgError(e) {
  e.target.style.display = 'none'
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDatasets()
})

const handleUpload = async (event, dataset) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  const formData = new FormData()
  for (let i = 0; i < files.length; i++) {
    formData.append('images', files[i])
  }
  formData.append('dataset', dataset.id)
  try {
    const res = await datasetApi.uploadImages(formData)
    alert('上传成功，返回：' + JSON.stringify(res.data))
  } catch (err) {
    alert('上传失败')
  }
}
const triggerUpload = (dataset) => {
  document.getElementById('upload-' + dataset.id).click()
}
</script>

<style scoped>
.dataset-overview {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 80px);
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 数据集区域 */
.datasets-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
}

.datasets-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

@media (max-width: 1200px) {
  .datasets-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .datasets-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

/* 数据集卡片 */
.dataset-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.dataset-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.dataset-card.active {
  border: 2px solid #667eea;
  background: rgba(102, 126, 234, 0.05);
}

/* 数据集头部 */
.dataset-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.dataset-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 1rem;
}

.dataset-info {
  flex: 1;
}

.dataset-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.dataset-subtitle {
  margin: 0.25rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
}

.dataset-menu {
  position: relative;
}

.menu-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  color: #666;
  transition: background 0.2s;
}

.menu-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.menu-button svg {
  width: 20px;
  height: 20px;
}

/* 预览区域 */
.dataset-preview {
  margin-bottom: 1rem;
  height: 120px;
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dataset-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  margin: auto;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
              linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
              linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
              linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

.preview-shapes {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.shape {
  width: 24px;
  height: 24px;
}

.triangle {
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-bottom: 20px solid #999;
}

.square {
  background: #999;
}

.circle {
  background: #999;
  border-radius: 50%;
}

/* 内容区域 */
.dataset-content {
  margin-bottom: 1.5rem;
}

.content-title {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.content-subtitle {
  margin: 0 0 0.5rem 0;
  color: #666;
  font-size: 0.9rem;
}

.content-description {
  margin: 0;
  color: #666;
  font-size: 0.85rem;
  line-height: 1.4;
}

/* 操作按钮 */
.dataset-actions {
  display: flex;
  gap: 0.75rem;
}

.action-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.action-button.secondary {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.action-button.secondary:hover {
  background: rgba(102, 126, 234, 0.2);
}

.action-button.primary {
  background: #667eea;
  color: white;
}

.action-button.primary:hover {
  background: #5a6fd8;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dataset-overview {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}
</style>
