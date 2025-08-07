// stores/analytics.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
export interface TrafficData {
  date: string
  total_requests: number
  distinct_ips: number
  transcribe_count: number
  report_count: number
  treatment_count: number
  error_count: number
  success_rate: number
  avg_processing_time: number
  total_file_size: number
}

export interface ErrorLog {
  timestamp: string
  ip: string
  endpoint: string
  method: string
  error_message: string
  processing_time: number
}

export interface ModelUsageStats {
  [key: string]: {
    usage_count: number
    avg_processing_time: number
  }
}

export const useAnalyticsStore = defineStore('analytics', () => {
  // 狀態
  const trafficData = ref<TrafficData[]>([])
  const errorLogs = ref<ErrorLog[]>([])
  const modelUsageStats = ref<ModelUsageStats>({})
  const loading = ref(false)

  // API 基礎 URL - 請根據您的實際後端地址調整

  // 動作
  const fetchTrafficData = async (startDate: string, endDate: string) => {
    loading.value = true
    try {
      const response = await fetch(
        `${API_BASE_URL}/backend/traffic?start=${startDate}&end=${endDate}`
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '獲取流量數據失敗')
      }

      const data = await response.json()
      trafficData.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch traffic data:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchErrorLogs = async (limit: number = 50) => {
    try {
      const response = await fetch(`${API_BASE_URL}/errors?limit=${limit}`)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '獲取錯誤日誌失敗')
      }

      const data = await response.json()
      errorLogs.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch error logs:', error)
      throw error
    }
  }

  const fetchModelUsageStats = async (days: number = 30) => {
    try {
      const response = await fetch(`${API_BASE_URL}/models?days=${days}`)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '獲取模型使用統計失敗')
      }

      const data = await response.json()
      modelUsageStats.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch model usage stats:', error)
      throw error
    }
  }

  // 計算屬性輔助函數
  const getTotalRequests = () => {
    return trafficData.value.reduce((sum, day) => sum + day.total_requests, 0)
  }

  const getTotalDistinctIps = () => {
    if (trafficData.value.length === 0) return 0
    // 獲取最大的獨立IP數（因為IP可能在多天重複）
    return Math.max(...trafficData.value.map((day) => day.distinct_ips))
  }

  const getOverallSuccessRate = () => {
    if (trafficData.value.length === 0) return 0
    const totalRequests = getTotalRequests()
    const totalErrors = trafficData.value.reduce((sum, day) => sum + day.error_count, 0)
    return totalRequests > 0 ? Math.round(((totalRequests - totalErrors) / totalRequests) * 100) : 0
  }

  const getAverageProcessingTime = () => {
    if (trafficData.value.length === 0) return 0
    const sum = trafficData.value.reduce((sum, day) => sum + day.avg_processing_time, 0)
    return Math.round(sum / trafficData.value.length)
  }

  const getApiEndpointStats = () => {
    return trafficData.value.reduce(
      (acc, day) => ({
        transcribe: acc.transcribe + day.transcribe_count,
        report: acc.report + day.report_count,
        treatment: acc.treatment + day.treatment_count
      }),
      { transcribe: 0, report: 0, treatment: 0 }
    )
  }

  // 清理數據
  const clearData = () => {
    trafficData.value = []
    errorLogs.value = []
    modelUsageStats.value = {}
  }

  return {
    // 狀態
    trafficData,
    errorLogs,
    modelUsageStats,
    loading,

    // 動作
    fetchTrafficData,
    fetchErrorLogs,
    fetchModelUsageStats,
    clearData,

    // 計算屬性輔助函數
    getTotalRequests,
    getTotalDistinctIps,
    getOverallSuccessRate,
    getAverageProcessingTime,
    getApiEndpointStats
  }
})
