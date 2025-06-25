import axios from 'axios'

// 配置 axios 基础设置
const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 索引构建相关 API
export const indexApi = {
  // 构建索引
  buildIndex(dataset_names, distributed = false) {
    return api.post('/build_index', {
      dataset_names,
      distributed
    })
  },
  
  // 获取构建进度
  getProgress(progressUrl) {
    return axios.get(progressUrl)
  }
}

// 图片检索相关 API
export const searchApi = {
  // 图片检索
  searchImage(formData) {
    return api.post('/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 数据集相关 API
export const datasetApi = {
  // 获取数据集ID
  getDatasetId(name) {
    return api.post('/get_dataset_id', { name })
  },
  
  // 获取所有数据集列表
  getDatasets() {
    return api.get('/datasets')
  },
  
  // 上传图片到数据集
  uploadImages(formData) {
    return api.post('/upload_images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 重复图片检测相关 API
export const duplicateApi = {
  // 查找重复图片
  findDuplicates(index_id, threshold, deduplicate = false) {
    return api.post('/repeated_search', {
      index_id,
      threshold,
      deduplicate
    })
  }
}

export default api
