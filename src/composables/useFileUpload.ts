// composables/useFileUpload.ts
import { ref } from 'vue'
import { useProjectStore } from '@/stores/useProjectStore'
import { fileUtils } from '@/utils/fileUtils'

interface AudioUploadResult {
  file: File
  url: string
}

interface TranscriptUploadResult {
  content: string
}

export function useFileUpload() {
  const projectStore = useProjectStore()
  const isProcessing = ref<boolean>(false)
  
  // 處理音檔上傳
  const handleAudioUpload = async (file: File): Promise<AudioUploadResult> => {
    try {
      isProcessing.value = true
      
      // 驗證檔案
      const validation = fileUtils.validateAudioFile(file)
      if (!validation.isValid) {
        throw new Error(validation.message)
      }
      
      // 創建音檔 URL
      const audioUrl = URL.createObjectURL(file)
      
      // 設置到 store
      projectStore.setAudioFile(file, audioUrl)
      
      return { file, url: audioUrl }
      
    } catch (error) {
      console.error('音檔上傳失敗:', error)
      throw error
    } finally {
      isProcessing.value = false
    }
  }
  
  // 處理逐字稿上傳
  const handleTranscriptUpload = async (file: File): Promise<TranscriptUploadResult> => {
    try {
      isProcessing.value = true
      
      // 驗證檔案
      const validation = fileUtils.validateTextFile(file)
      if (!validation.isValid) {
        throw new Error(validation.message)
      }
      
      // 讀取檔案內容
      const content = await fileUtils.readTextFile(file)
      
      // 設置到 store
      projectStore.setTranscript(content)
      
      return { content }
      
    } catch (error) {
      console.error('逐字稿上傳失敗:', error)
      throw error
    } finally {
      isProcessing.value = false
    }
  }
  
  return {
    isProcessing,
    handleAudioUpload,
    handleTranscriptUpload
  }
}