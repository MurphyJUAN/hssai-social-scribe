// services/apiService.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5353'

interface SSEData {
  type: 'progress' | 'chunk' | 'complete' | 'error'
  progress?: number
  text?: string
  error?: string
}

interface ReportGenerationData {
  transcript: string
  socialWorkerNotes: string
  selectedSections: string[]
  requiredSections: string[]
}

interface TreatmentGenerationData {
  transcript: string
  reportDraft: string
  selectedServiceDomains: string[]
  socialWorkerNotes: string
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分鐘超時，因為AI生成可能需要較長時間
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在這裡添加認證 token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 響應攔截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const apiService = {
  // ==================== 音檔轉逐字稿 ====================
  async transcribeAudio(
    audioFile: File,
    onProgress?: (progress: number, partialTranscript?: string) => void
  ): Promise<string> {
    const formData = new FormData()
    formData.append('audio', audioFile)

    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/api/transcribe`, {
        method: 'POST',
        body: formData
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }

          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('無法讀取響應數據')
          }

          const decoder = new TextDecoder()
          let transcript = ''

          function readStream(): void {
            reader
              .read()
              .then(({ done, value }) => {
                if (done) {
                  resolve(transcript)
                  return
                }

                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split('\n')

                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    try {
                      const data: SSEData = JSON.parse(line.slice(6))

                      if (data.type === 'progress') {
                        onProgress?.(data.progress || 0)
                      } else if (data.type === 'chunk') {
                        transcript += data.text || ''
                        onProgress?.(data.progress || 0, transcript)
                      } else if (data.type === 'complete') {
                        resolve(transcript)
                        return
                      } else if (data.type === 'error') {
                        reject(new Error(data.error || '轉換失敗'))
                        return
                      }
                    } catch (e) {
                      console.warn('Failed to parse SSE data:', line)
                    }
                  }
                }

                readStream()
              })
              .catch(reject)
          }

          readStream()
        })
        .catch(reject)
    })
  },

  // ==================== 生成記錄初稿 ====================
  async generateReport(
    data: ReportGenerationData,
    onProgress?: (progress: number, partialReport?: string) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/api/generate-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }

          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('無法讀取響應數據')
          }

          const decoder = new TextDecoder()
          let reportContent = ''

          function readStream(): void {
            reader
              .read()
              .then(({ done, value }) => {
                if (done) {
                  resolve(reportContent)
                  return
                }

                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split('\n')

                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    try {
                      const data: SSEData = JSON.parse(line.slice(6))

                      if (data.type === 'progress') {
                        onProgress?.(data.progress || 0)
                      } else if (data.type === 'chunk') {
                        reportContent += data.text || ''
                        onProgress?.(data.progress || 0, reportContent)
                      } else if (data.type === 'complete') {
                        resolve(reportContent)
                        return
                      } else if (data.type === 'error') {
                        reject(new Error(data.error || '生成失敗'))
                        return
                      }
                    } catch (e) {
                      console.warn('Failed to parse SSE data:', line)
                    }
                  }
                }

                readStream()
              })
              .catch(reject)
          }

          readStream()
        })
        .catch(reject)
    })
  },

  // ==================== 生成處遇計畫 ====================
  async generateTreatmentPlan(
    data: TreatmentGenerationData,
    onProgress?: (progress: number, partialPlan?: string) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      fetch(`${API_BASE_URL}/api/generate-treatment-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }

          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('無法讀取響應數據')
          }

          const decoder = new TextDecoder()
          let planContent = ''

          function readStream(): void {
            reader
              .read()
              .then(({ done, value }) => {
                if (done) {
                  resolve(planContent)
                  return
                }

                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split('\n')

                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    try {
                      const data: SSEData = JSON.parse(line.slice(6))

                      if (data.type === 'progress') {
                        onProgress?.(data.progress || 0)
                      } else if (data.type === 'chunk') {
                        planContent += data.text || ''
                        onProgress?.(data.progress || 0, planContent)
                      } else if (data.type === 'complete') {
                        resolve(planContent)
                        return
                      } else if (data.type === 'error') {
                        reject(new Error(data.error || '生成失敗'))
                        return
                      }
                    } catch (e) {
                      console.warn('Failed to parse SSE data:', line)
                    }
                  }
                }

                readStream()
              })
              .catch(reject)
          }

          readStream()
        })
        .catch(reject)
    })
  }
}

// utils/fileUtils.ts
export interface FileValidationResult {
  isValid: boolean
  message: string
}

export const fileUtils = {
  // 下載文字檔案
  downloadTextFile(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  },

  // 讀取文字檔案
  readTextFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result
        if (typeof result === 'string') {
          resolve(result)
        } else {
          reject(new Error('無法讀取檔案內容'))
        }
      }
      reader.onerror = () => reject(new Error('檔案讀取失敗'))
      reader.readAsText(file, 'UTF-8')
    })
  },

  // 驗證音檔格式
  validateAudioFile(file: File): FileValidationResult {
    const validTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/ogg', 'audio/mpeg']
    const maxSize = 100 * 1024 * 1024 // 100MB

    if (!validTypes.includes(file.type)) {
      return {
        isValid: false,
        message: '不支援的音檔格式，請上傳 MP3、WAV、M4A 或 OGG 格式'
      }
    }

    if (file.size > maxSize) {
      return {
        isValid: false,
        message: '音檔大小不能超過 100MB'
      }
    }

    return { isValid: true, message: '音檔格式有效' }
  },

  // 驗證文字檔案
  validateTextFile(file: File): FileValidationResult {
    const validTypes = ['text/plain', 'application/txt']
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!validTypes.includes(file.type) && !file.name.endsWith('.txt')) {
      return {
        isValid: false,
        message: '請上傳 .txt 格式的文字檔案'
      }
    }

    if (file.size > maxSize) {
      return {
        isValid: false,
        message: '文字檔案大小不能超過 10MB'
      }
    }

    return { isValid: true, message: '文字檔案格式有效' }
  },

  // 格式化檔案大小
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // 生成檔案名稱
  generateFileName(type: string, extension: string = 'txt'): string {
    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10)
    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '-')
    return `${type}_${dateStr}_${timeStr}.${extension}`
  }
}

// utils/audioUtils.ts
export const audioUtils = {
  // 格式化時間顯示
  formatTime(seconds: number): string {
    if (isNaN(seconds)) return '00:00'

    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  },

  // 創建音檔 URL
  createAudioUrl(file: File): string {
    return URL.createObjectURL(file)
  },

  // 釋放音檔 URL
  revokeAudioUrl(url: string): void {
    if (url) {
      URL.revokeObjectURL(url)
    }
  }
}

// utils/validationUtils.ts
export interface ValidationResult {
  isValid: boolean
  message: string
}

export const validationUtils = {
  // 驗證逐字稿內容
  validateTranscript(transcript: string): ValidationResult {
    if (!transcript || typeof transcript !== 'string') {
      return { isValid: false, message: '逐字稿內容不能為空' }
    }

    if (transcript.trim().length < 10) {
      return { isValid: false, message: '逐字稿內容過短，至少需要10個字元' }
    }

    return { isValid: true, message: '逐字稿內容有效' }
  },

  // 驗證記錄設定
  validateReportConfig(selectedSections: string[], requiredSections: string[]): ValidationResult {
    if (selectedSections.length === 0 && requiredSections.length === 0) {
      return { isValid: false, message: '請至少選擇一個記錄段落' }
    }

    return { isValid: true, message: '記錄設定有效' }
  },

  // 驗證處遇計畫設定
  validateTreatmentConfig(
    selectedGoals: string[],
    selectedMethods: string[],
    timeframe: string
  ): ValidationResult {
    if (selectedGoals.length === 0) {
      return { isValid: false, message: '請至少選擇一個處遇目標' }
    }

    if (selectedMethods.length === 0) {
      return { isValid: false, message: '請至少選擇一個處遇方法' }
    }

    if (!timeframe) {
      return { isValid: false, message: '請選擇處遇時程' }
    }

    return { isValid: true, message: '處遇計畫設定有效' }
  }
}
