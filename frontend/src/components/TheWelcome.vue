<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'

const queryImg = ref(null)
const previewUrl = ref('')
const crop = ref({ x: 0, y: 0, w: 0, h: 0 })
const results = ref([])
const buildMsg = ref('')
const uploading = ref(false)
const canvasRef = ref(null)
let imgObj = null

// 新增：用于临时显示正在绘制的框
let drawingRect = null
const datasetNames = ref(['']) // 支持多个数据集名称

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  queryImg.value = file
  const reader = new FileReader()
  reader.onload = ev => {
    previewUrl.value = ev.target.result
    nextTick(() => drawImage())
  }
  reader.readAsDataURL(file)
}

function drawImage(rect) {
  if (!previewUrl.value) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  imgObj = new window.Image()
  imgObj.onload = () => {
    canvas.width = imgObj.width
    canvas.height = imgObj.height
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(imgObj, 0, 0)
    // 如果有临时框，绘制
    if (rect) {
      ctx.strokeStyle = '#42b983'
      ctx.lineWidth = 2
      ctx.strokeRect(rect.x, rect.y, rect.w, rect.h)
    }
  }
  imgObj.src = previewUrl.value
}

let startX, startY, isDown = false
function onMouseDown(ev) {
  isDown = true
  startX = ev.offsetX
  startY = ev.offsetY
  // 监听 mousemove
  const canvas = canvasRef.value
  canvas.addEventListener('mousemove', onMouseMove)
}
function onMouseUp(ev) {
  if (!isDown) return
  isDown = false
  const endX = ev.offsetX
  const endY = ev.offsetY
  const x = Math.min(startX, endX)
  const y = Math.min(startY, endY)
  const w = Math.abs(endX - startX)
  const h = Math.abs(endY - startY)
  crop.value = { x, y, w, h }
  // 画最终框
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(imgObj, 0, 0)
  ctx.strokeStyle = '#42b983'
  ctx.lineWidth = 2
  ctx.strokeRect(x, y, w, h)
  // 移除 mousemove 监听
  canvas.removeEventListener('mousemove', onMouseMove)
  drawingRect = null
}

// 新增：鼠标移动时动态画框
function onMouseMove(ev) {
  if (!isDown) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(imgObj, 0, 0)
  const currX = ev.offsetX
  const currY = ev.offsetY
  const x = Math.min(startX, currX)
  const y = Math.min(startY, currY)
  const w = Math.abs(currX - startX)
  const h = Math.abs(currY - startY)
  ctx.strokeStyle = '#42b983'
  ctx.lineWidth = 2
  ctx.strokeRect(x, y, w, h)
  drawingRect = { x, y, w, h }
}

function addDataset() {
  datasetNames.value.push('')
}
function removeDataset(idx) {
  if (datasetNames.value.length > 1) {
    datasetNames.value.splice(idx, 1)
  }
}

async function buildIndex(distributed = false) {
  buildMsg.value = '正在构建索引...'
  // 收集所有非空数据集名称
  const names = datasetNames.value.filter(name => !!name)
  if (!names.length) {
    buildMsg.value = '请填写数据集名称'
    return
  }
  const url = distributed ? '/api/build_index_distributed' : '/api/build_index'
  try {
    const resp = await axios.post(url, {
      dataset_names: names,
      distributed: distributed
    })
    buildMsg.value = resp.data.msg
  } catch (e) {
    buildMsg.value = '构建索引失败'
  }
}

async function submitSearch() {
  if (!queryImg.value) return
  uploading.value = true
  buildMsg.value = ''
  results.value = []
  const form = new FormData()
  form.append('query_img', queryImg.value)
  form.append('crop_x', crop.value.x)
  form.append('crop_y', crop.value.y)
  form.append('crop_w', crop.value.w)
  form.append('crop_h', crop.value.h)
  // 新增：支持多个数据集名称（后端建议用 dataset_names[] 作为 key）
  datasetNames.value.forEach(name => {
    if (name) form.append('dataset_names[]', name)
  })
  try {
    const resp = await axios.post('/api/search', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    results.value = resp.data.results || []
  } catch (e) {
    buildMsg.value = '检索失败'
  }
  uploading.value = false
}

const repeatedGroups = ref([])
const repMsg = ref('')
const repLoading = ref(false)
const repThreshold = ref(95)

async function findRepeated() {
  repMsg.value = ''
  repeatedGroups.value = []
  repLoading.value = true
  // 只用第一个数据集名称（可自行扩展为多数据集）
  const dsName = datasetNames.value[0]
  if (!dsName) {
    repMsg.value = '请填写数据集名称'
    repLoading.value = false
    return
  }
  // 获取数据集id
  try {
    const dsResp = await axios.post('/api/get_dataset_id', { name: dsName })
    const dsId = dsResp.data.id
    const resp = await axios.post('/api/repeated_search', {
      index_id: dsId,
      threshold: repThreshold.value,
      deduplicate: false
    })
    repeatedGroups.value = resp.data.groups || []
    if (!repeatedGroups.value.length) {
      repMsg.value = '未检测到重复图片'
    }
  } catch (e) {
    repMsg.value = '查重失败'
  }
  repLoading.value = false
}
</script>

<template>
  <div class="upload-container">
    <h1 class="title">图片检索系统</h1>
    <div class="upload-panel">
      <div style="margin-bottom: 1rem; width: 100%;">
        <div v-for="(name, idx) in datasetNames" :key="idx" style="display: flex; align-items: center; margin-bottom: 0.3rem;">
          <input
            class="dataset-input"
            type="text"
            v-model="datasetNames[idx]"
            :placeholder="`请输入数据集名称${datasetNames.length > 1 ? '（可多选）' : ''}`"
            style="width: 220px; padding: 0.4rem;"
          />
          <button v-if="datasetNames.length > 1" class="btn" style="margin-left: 0.5rem; padding: 0.2rem 0.7rem;" @click="removeDataset(idx)">-</button>
        </div>
        <button class="btn" style="padding: 0.2rem 0.7rem;" @click="addDataset">+</button>
      </div>
      <input class="file-input" type="file" accept="image/*" @change="onFileChange" />
      <div class="btn-group">
        <button class="btn" @click="buildIndex(false)">本地构建索引</button>
        <button class="btn" @click="buildIndex(true)">远程构建索引</button>
      </div>
      <div v-if="buildMsg" class="msg">{{ buildMsg }}</div>
      <canvas
        ref="canvasRef"
        id="preview-canvas"
        class="preview-canvas"
        @mousedown="onMouseDown"
        @mouseup="onMouseUp"
      ></canvas>
      <button class="btn main-btn" :disabled="!queryImg || uploading" @click="submitSearch">
        {{ uploading ? '检索中...' : '上传并检索' }}
      </button>
    </div>
    <div v-if="results.length" class="result-panel">
      <h2>检索结果</h2>
      <ol>
        <li v-for="item in results" :key="item.idx + '-' + item.dataset" class="result-item">
          <img :src="item.img_url" class="result-img" />
          <div class="result-info">
            {{ item.fname }} (编号: {{ item.idx }}) <span v-if="item.dataset">[{{ item.dataset }}]</span>
            <span v-if="item.similarity !== undefined">
              | 相似度: {{ item.similarity.toFixed(2) }}%
            </span>
            <!-- 新增：输出描述 -->
            <div v-if="item.description && Object.keys(item.description).length" class="desc-info">
              <span v-for="(val, key) in item.description" :key="key" style="display:inline-block;margin-right:1em;">
                <b>{{ key }}:</b> {{ val }}
              </span>
            </div>
          </div>
        </li>
      </ol>
    </div>
    <div style="margin-top:2rem;width:100%;text-align:left;">
      <h2 style="font-size:1.08rem;">查找重复图片</h2>
      <div style="display:flex;align-items:center;gap:0.5em;">
        <label>相似度阈值：</label>
        <input type="number" v-model="repThreshold" min="80" max="100" step="1" style="width:60px;" />
        <button class="btn" :disabled="repLoading" @click="findRepeated">
          {{ repLoading ? '查重中...' : '查找重复图片' }}
        </button>
        <span style="color:#888;font-size:0.96em;" v-if="repMsg">{{ repMsg }}</span>
      </div>
      <div v-if="repeatedGroups.length" class="repeated-result">
        <ol>
          <li v-for="(group, idx) in repeatedGroups" :key="idx" style="margin-bottom:0.5em;">
            <b>重复组 {{ idx + 1 }}：</b>
            <span v-for="id in group" :key="id" style="margin-right:0.8em;">图片ID: {{ id }}</span>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-container {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 6px 32px 0 rgba(60,60,60,0.10);
  padding: 2.5rem 2rem 2rem 2rem;
  width: 96vw;
  max-width: 75vw;
  min-width: 320px;
  margin: 3rem auto 2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}
.title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2d8cf0;
  margin-bottom: 1.5rem;
  letter-spacing: 2px;
}
.upload-panel {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.file-input {
  margin-bottom: 1.2rem;
}
.btn-group {
  display: flex;
  gap: 0.7rem;
  margin-bottom: 1.2rem;
}
.btn {
  background: linear-gradient(90deg, #2d8cf0 0%, #42b983 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.55rem 1.4rem;
  font-size: 1.05rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px 0 rgba(60,60,60,0.06);
}
.btn:hover:enabled {
  background: linear-gradient(90deg, #42b983 0%, #2d8cf0 100%);
}
.main-btn {
  margin-top: 1.5rem;
  width: 100%;
  font-size: 1.15rem;
  font-weight: bold;
  letter-spacing: 1px;
}
.btn:disabled {
  background: #b5e2d4;
  cursor: not-allowed;
  opacity: 0.7;
}
.msg {
  color: #2d8cf0;
  margin-bottom: 1rem;
  font-size: 1.05rem;
  min-height: 1.2em;
}
.preview-canvas {
  margin: 0.7rem 0 0.7rem 0;
  width: 100%;
  max-width: 340px;
  max-height: 340px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #f8fafc;
  box-shadow: 0 2px 8px 0 rgba(60,60,60,0.04);
  display: block;
}
.result-panel {
  margin-top: 2.5rem;
  width: 100%;
}
.result-panel h2 {
  font-size: 1.18rem;
  color: #333;
  margin-bottom: 1rem;
  font-weight: 600;
}
.result-item {
  display: flex;
  align-items: center;
  margin-bottom: 1.1rem;
  background: #f6fefb;
  border-radius: 10px;
  padding: 0.7rem;
  box-shadow: 0 1px 4px 0 rgba(60,60,60,0.04);
  transition: box-shadow 0.2s;
}
.result-item:hover {
  box-shadow: 0 4px 16px 0 rgba(60,60,60,0.10);
}
.result-img {
  max-width: 90px;
  max-height: 90px;
  border: 1.5px solid #b5e2d4;
  border-radius: 6px;
  margin-right: 1.2rem;
  background: #fff;
}
.result-info {
  font-size: 1.08rem;
  color: #222;
  word-break: break-all;
}
.desc-info {
  margin-top: 0.3em;
  color: #666;
  font-size: 0.98em;
}
.repeated-result {
  margin-top: 1em;
  background: #f8fafc;
  border-radius: 8px;
  padding: 1em;
  font-size: 1.01em;
}
@media (max-width: 500px) {
  .upload-container {
    max-width: 98vw;
    min-width: 0;
    padding: 1.2rem 0.5rem 1rem 0.5rem;
  }
  .preview-canvas {
    max-width: 98vw;
    min-width: 0;
  }
}
</style>
