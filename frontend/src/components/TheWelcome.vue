<script setup>
import { ref, nextTick } from 'vue'

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

async function buildIndex(distributed = false) {
  buildMsg.value = '正在构建索引...'
  const url = distributed ? '/api/build_index_distributed' : '/api/build_index'
  const resp = await fetch(url, { method: 'POST' })
  const data = await resp.json()
  buildMsg.value = data.msg
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
  const resp = await fetch('/api/search', { method: 'POST', body: form })
  const data = await resp.json()
  results.value = data.results || []
  uploading.value = false
}
</script>

<template>
  <div class="upload-container">
    <h1 class="title">图片检索系统</h1>
    <div class="upload-panel">
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
        <li v-for="item in results" :key="item.idx" class="result-item">
          <img :src="item.img_url" class="result-img" />
          <div class="result-info">{{ item.fname }} (编号: {{ item.idx }})</div>
        </li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.upload-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(60,60,60,0.08);
  padding: 2.5rem 2rem 2rem 2rem;
  width: 100%;
  max-width: 600px;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}
.title {
  font-size: 2rem;
  font-weight: bold;
  color: #42b983;
  margin-bottom: 1.2rem;
  letter-spacing: 2px;
}
.upload-panel {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.file-input {
  margin-bottom: 1rem;
}
.btn-group {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.btn {
  background: #42b983;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn:hover:enabled {
  background: #369870;
}
.main-btn {
  margin-top: 1.2rem;
  width: 100%;
  font-size: 1.1rem;
  font-weight: bold;
}
.btn:disabled {
  background: #b5e2d4;
  cursor: not-allowed;
}
.msg {
  color: #369870;
  margin-bottom: 0.8rem;
  font-size: 1rem;
  min-height: 1.2em;
}
.preview-canvas {
  margin: 0.5rem 0 0.5rem 0;
  max-width: 320px;
  max-height: 320px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  box-shadow: 0 2px 8px 0 rgba(60,60,60,0.04);
}
.result-panel {
  margin-top: 2rem;
  width: 100%;
}
.result-panel h2 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 0.8rem;
}
.result-item {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  background: #f6fefb;
  border-radius: 8px;
  padding: 0.5rem;
  box-shadow: 0 1px 4px 0 rgba(60,60,60,0.03);
}
.result-img {
  max-width: 80px;
  max-height: 80px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 1rem;
  background: #fff;
}
.result-info {
  font-size: 1rem;
  color: #222;
}
</style>
