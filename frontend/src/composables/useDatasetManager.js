import { ref } from 'vue'

/**
 * 数据集管理相关的 composable
 */
export function useDatasetManager() {
  const datasetNames = ref([''])

  /**
   * 添加数据集
   */
  function addDataset() {
    datasetNames.value.push('')
  }

  /**
   * 删除数据集
   */
  function removeDataset(index) {
    if (datasetNames.value.length > 1) {
      datasetNames.value.splice(index, 1)
    }
  }

  /**
   * 获取有效的数据集名称列表
   */
  function getValidDatasetNames() {
    return datasetNames.value.filter(name => !!name.trim())
  }

  /**
   * 验证数据集名称
   */
  function validateDatasets() {
    const validNames = getValidDatasetNames()
    return {
      isValid: validNames.length > 0,
      names: validNames,
      message: validNames.length === 0 ? '请填写至少一个数据集名称' : ''
    }
  }

  return {
    datasetNames,
    addDataset,
    removeDataset,
    getValidDatasetNames,
    validateDatasets
  }
}
