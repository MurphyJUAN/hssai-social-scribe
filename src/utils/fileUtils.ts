// utils/fileUtils.ts

/**
 * 檔案驗證結果介面
 */
export interface FileValidationResult {
  isValid: boolean
  message: string
}

/**
 * 支援的音檔格式
 */
export const SUPPORTED_AUDIO_TYPES = [
  'audio/mp3',
  'audio/mpeg',
  'audio/wav',
  'audio/wave',
  'audio/x-wav',
  'audio/m4a',
  'audio/mp4',
  'audio/aac',
  'audio/ogg',
  'audio/webm',
  'audio/flac'
] as const

/**
 * 支援的文字檔格式
 */
export const SUPPORTED_TEXT_TYPES = ['text/plain', 'application/txt', 'text/txt'] as const

/**
 * 檔案大小限制（位元組）
 */
export const FILE_SIZE_LIMITS = {
  AUDIO: 200 * 1024 * 1024, // 200MB
  TEXT: 50 * 1024 * 1024, // 50MB
  IMAGE: 10 * 1024 * 1024 // 10MB
} as const

/**
 * 檔案工具函數集合
 */
export const fileUtils = {
  /**
   * 下載文字檔案
   * @param content 檔案內容
   * @param filename 檔案名稱
   * @param mimeType MIME 類型
   */
  downloadTextFile(
    content: string,
    filename: string,
    mimeType: string = 'text/plain;charset=utf-8'
  ): void {
    try {
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')

      link.href = url
      link.download = filename
      link.style.display = 'none'

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // 清理 URL 物件
      setTimeout(() => URL.revokeObjectURL(url), 100)
    } catch (error) {
      console.error('下載檔案失敗:', error)
      throw new Error('檔案下載失敗，請稍後再試')
    }
  },

  /**
   * 下載 JSON 檔案
   * @param data 要下載的資料
   * @param filename 檔案名稱
   */
  downloadJsonFile(data: any, filename: string): void {
    try {
      const jsonString = JSON.stringify(data, null, 2)
      this.downloadTextFile(jsonString, filename, 'application/json;charset=utf-8')
    } catch (error) {
      console.error('下載 JSON 檔案失敗:', error)
      throw new Error('JSON 檔案下載失敗')
    }
  },

  /**
   * 讀取文字檔案
   * @param file 檔案物件
   * @param encoding 編碼格式
   * @returns Promise<string> 檔案內容
   */
  readTextFile(file: File, encoding: string = 'UTF-8'): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        const reader = new FileReader()

        reader.onload = (event) => {
          const result = event.target?.result
          if (typeof result === 'string') {
            resolve(result)
          } else {
            reject(new Error('檔案讀取結果格式錯誤'))
          }
        }

        reader.onerror = () => {
          reject(new Error('檔案讀取失敗'))
        }

        reader.onabort = () => {
          reject(new Error('檔案讀取被中斷'))
        }

        reader.readAsText(file, encoding)
      } catch (error) {
        reject(new Error('檔案讀取過程發生錯誤'))
      }
    })
  },

  /**
   * 讀取檔案為 ArrayBuffer
   * @param file 檔案物件
   * @returns Promise<ArrayBuffer> 檔案資料
   */
  readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
    return new Promise((resolve, reject) => {
      try {
        const reader = new FileReader()

        reader.onload = (event) => {
          const result = event.target?.result
          if (result instanceof ArrayBuffer) {
            resolve(result)
          } else {
            reject(new Error('檔案讀取結果格式錯誤'))
          }
        }

        reader.onerror = () => {
          reject(new Error('檔案讀取失敗'))
        }

        reader.readAsArrayBuffer(file)
      } catch (error) {
        reject(new Error('檔案讀取過程發生錯誤'))
      }
    })
  },

  /**
   * 讀取檔案為 Base64
   * @param file 檔案物件
   * @returns Promise<string> Base64 字串
   */
  readFileAsBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        const reader = new FileReader()

        reader.onload = (event) => {
          const result = event.target?.result
          if (typeof result === 'string') {
            // 移除 data:mime;base64, 前綴
            const base64 = result.split(',')[1] || result
            resolve(base64)
          } else {
            reject(new Error('檔案讀取結果格式錯誤'))
          }
        }

        reader.onerror = () => {
          reject(new Error('檔案讀取失敗'))
        }

        reader.readAsDataURL(file)
      } catch (error) {
        reject(new Error('檔案讀取過程發生錯誤'))
      }
    })
  },

  /**
   * 驗證音檔格式
   * @param file 檔案物件
   * @returns FileValidationResult 驗證結果
   */
  validateAudioFile(file: File): FileValidationResult {
    // 檢查檔案是否存在
    if (!file) {
      return {
        isValid: false,
        message: '請選擇一個檔案'
      }
    }

    // 檢查檔案類型
    const isValidType =
      SUPPORTED_AUDIO_TYPES.includes(file.type as any) ||
      file.name.toLowerCase().match(/\.(mp3|wav|m4a|aac|ogg|flac|webm)$/)

    if (!isValidType) {
      return {
        isValid: false,
        message: '不支援的音檔格式。支援格式：MP3、WAV、M4A、AAC、OGG、FLAC'
      }
    }

    // 檢查檔案大小
    if (file.size > FILE_SIZE_LIMITS.AUDIO) {
      return {
        isValid: false,
        message: `音檔大小不能超過 ${this.formatFileSize(FILE_SIZE_LIMITS.AUDIO)}`
      }
    }

    // 檢查檔案大小下限（避免空檔案）
    if (file.size < 1024) {
      // 1KB
      return {
        isValid: false,
        message: '音檔檔案過小，請確認檔案是否正確'
      }
    }

    return {
      isValid: true,
      message: '音檔格式有效'
    }
  },

  /**
   * 驗證文字檔案
   * @param file 檔案物件
   * @returns FileValidationResult 驗證結果
   */
  validateTextFile(file: File): FileValidationResult {
    // 檢查檔案是否存在
    if (!file) {
      return {
        isValid: false,
        message: '請選擇一個檔案'
      }
    }

    // 檢查檔案類型
    const isValidType =
      SUPPORTED_TEXT_TYPES.includes(file.type as any) || file.name.toLowerCase().endsWith('.txt')

    if (!isValidType) {
      return {
        isValid: false,
        message: '請上傳 .txt 格式的文字檔案'
      }
    }

    // 檢查檔案大小
    if (file.size > FILE_SIZE_LIMITS.TEXT) {
      return {
        isValid: false,
        message: `文字檔案大小不能超過 ${this.formatFileSize(FILE_SIZE_LIMITS.TEXT)}`
      }
    }

    // 檢查檔案大小下限
    if (file.size === 0) {
      return {
        isValid: false,
        message: '檔案為空，請選擇包含內容的文字檔案'
      }
    }

    return {
      isValid: true,
      message: '文字檔案格式有效'
    }
  },

  /**
   * 格式化檔案大小顯示
   * @param bytes 位元組數
   * @param decimals 小數位數
   * @returns string 格式化後的大小
   */
  formatFileSize(bytes: number, decimals: number = 2): string {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']

    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
  },

  /**
   * 生成檔案名稱
   * @param prefix 檔案前綴
   * @param extension 副檔名
   * @param includeTime 是否包含時間
   * @returns string 檔案名稱
   */
  generateFileName(prefix: string, extension: string = 'txt', includeTime: boolean = true): string {
    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10) // YYYY-MM-DD

    if (includeTime) {
      const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '-') // HH-MM-SS
      return `${prefix}_${dateStr}_${timeStr}.${extension}`
    } else {
      return `${prefix}_${dateStr}.${extension}`
    }
  },

  /**
   * 生成唯一檔案名稱
   * @param prefix 檔案前綴
   * @param extension 副檔名
   * @returns string 唯一檔案名稱
   */
  generateUniqueFileName(prefix: string, extension: string = 'txt'): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 8)
    return `${prefix}_${timestamp}_${random}.${extension}`
  },

  /**
   * 獲取檔案副檔名
   * @param filename 檔案名稱
   * @returns string 副檔名（不含點號）
   */
  getFileExtension(filename: string): string {
    const lastDotIndex = filename.lastIndexOf('.')
    if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
      return ''
    }
    return filename.substring(lastDotIndex + 1).toLowerCase()
  },

  /**
   * 檢查檔案名稱是否安全
   * @param filename 檔案名稱
   * @returns boolean 是否安全
   */
  isSafeFilename(filename: string): boolean {
    // 檢查危險字符
    const dangerousChars = /[<>:"/\\|?*\x00-\x1f]/
    if (dangerousChars.test(filename)) {
      return false
    }

    // 檢查保留名稱（Windows）
    const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)/i
    if (reservedNames.test(filename)) {
      return false
    }

    // 檢查長度
    if (filename.length > 255) {
      return false
    }

    return true
  },

  /**
   * 清理檔案名稱
   * @param filename 原始檔案名稱
   * @returns string 清理後的檔案名稱
   */
  sanitizeFilename(filename: string): string {
    // 移除危險字符
    let sanitized = filename.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_')

    // 處理保留名稱
    const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)/i
    if (reservedNames.test(sanitized)) {
      sanitized = '_' + sanitized
    }

    // 限制長度
    if (sanitized.length > 255) {
      const ext = this.getFileExtension(sanitized)
      const nameWithoutExt = sanitized.substring(0, sanitized.lastIndexOf('.'))
      const maxNameLength = 255 - ext.length - 1
      sanitized = nameWithoutExt.substring(0, maxNameLength) + '.' + ext
    }

    return sanitized
  },

  /**
   * 創建檔案 URL
   * @param file 檔案物件
   * @returns string URL 字串
   */
  createFileUrl(file: File): string {
    return URL.createObjectURL(file)
  },

  /**
   * 釋放檔案 URL
   * @param url URL 字串
   */
  revokeFileUrl(url: string): void {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url)
    }
  },

  /**
   * 複製檔案內容到剪貼簿
   * @param content 要複製的內容
   * @returns Promise<boolean> 是否成功
   */
  async copyToClipboard(content: string): Promise<boolean> {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(content)
        return true
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = content
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        const result = document.execCommand('copy')
        textArea.remove()
        return result
      }
    } catch (error) {
      console.error('複製到剪貼簿失敗:', error)
      return false
    }
  },

  /**
   * 檢查瀏覽器是否支援某個檔案類型
   * @param mimeType MIME 類型
   * @returns boolean 是否支援
   */
  isMimeTypeSupported(mimeType: string): boolean {
    const audio = document.createElement('audio')
    const video = document.createElement('video')

    return !!(audio.canPlayType(mimeType) || video.canPlayType(mimeType))
  },

  /**
   * 壓縮文字內容（簡單的重複行移除）
   * @param content 原始內容
   * @returns string 壓縮後的內容
   */
  compressTextContent(content: string): string {
    const lines = content.split('\n')
    const uniqueLines: string[] = []
    let lastLine = ''

    for (const line of lines) {
      const trimmedLine = line.trim()
      if (trimmedLine !== lastLine || trimmedLine === '') {
        uniqueLines.push(line)
        lastLine = trimmedLine
      }
    }

    return uniqueLines.join('\n')
  }
}

export default fileUtils
