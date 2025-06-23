import { ref } from 'vue'

/**
 * 通用加载状态管理
 */
export function useLoading() {
  const loading = ref(false)
  const message = ref('')

  function setLoading(isLoading, msg = '') {
    loading.value = isLoading
    message.value = msg
  }

  function startLoading(msg = '加载中...') {
    setLoading(true, msg)
  }

  function stopLoading(msg = '') {
    setLoading(false, msg)
  }

  return {
    loading,
    message,
    setLoading,
    startLoading,
    stopLoading
  }
}

/**
 * 进度条管理
 */
export function useProgress() {
  const progress = ref(0)
  const status = ref('')
  const isVisible = ref(false)
  function setProgress(value, statusText = '') {
    progress.value = value
    status.value = statusText
    // 进度条在有进度值时显示，完成时短暂显示后隐藏
    if (statusText === 'done' && value === 100) {
      isVisible.value = true
      // 2秒后隐藏进度条
      setTimeout(() => {
        isVisible.value = false
      }, 2000)
    } else {
      isVisible.value = value > 0 && statusText !== 'done'
    }
  }

  function resetProgress() {
    progress.value = 0
    status.value = ''
    isVisible.value = false
  }

  function showProgress() {
    isVisible.value = true
  }

  function hideProgress() {
    isVisible.value = false
  }

  return {
    progress,
    status,
    isVisible,
    setProgress,
    resetProgress,
    showProgress,
    hideProgress
  }
}
