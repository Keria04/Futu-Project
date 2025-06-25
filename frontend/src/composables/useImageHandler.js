import { ref, reactive } from 'vue'

/**
 * 图片处理相关的 composable
 */
export function useImageHandler() {
  const previewUrl = ref('')
  const canvasRef = ref(null)
  const crop = reactive({ x: 0, y: 0, w: 0, h: 0 })
  
  let imgObj = null
  let startX, startY, isDown = false
  let drawingRect = null

  /**
   * 处理文件选择
   */
  function handleFileChange(file) {
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (ev) => {
      previewUrl.value = ev.target.result
      setTimeout(() => drawImage(), 50)
    }
    reader.readAsDataURL(file)
  }

  /**
   * 绘制图片到画布
   */
  function drawImage(rect) {
    if (!previewUrl.value || !canvasRef.value) return
    
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    imgObj = new Image()
    
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

  /**
   * 鼠标按下事件
   */
  function onMouseDown(ev) {
    isDown = true
    startX = ev.offsetX
    startY = ev.offsetY
    
    const canvas = canvasRef.value
    canvas.addEventListener('mousemove', onMouseMove)
  }

  /**
   * 鼠标抬起事件
   */
  function onMouseUp(ev) {
    if (!isDown) return
    isDown = false
    
    const endX = ev.offsetX
    const endY = ev.offsetY
    const x = Math.min(startX, endX)
    const y = Math.min(startY, endY)
    const w = Math.abs(endX - startX)
    const h = Math.abs(endY - startY)
    
    crop.x = x
    crop.y = y
    crop.w = w
    crop.h = h
    
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

  /**
   * 鼠标移动事件
   */
  function onMouseMove(ev) {
    if (!isDown || !canvasRef.value) return
    
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

  return {
    previewUrl,
    canvasRef,
    crop,
    handleFileChange,
    drawImage,
    onMouseDown,
    onMouseUp,
    onMouseMove
  }
}
