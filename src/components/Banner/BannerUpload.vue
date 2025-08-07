<template>
  <section
    class="relative text-white text-center overflow-hidden transition-all duration-500"
    :class="store.hasUploaded ? 'h-[400px]' : 'h-[calc(100vh)]'"
  >
    <!-- 背景圖層 -->
    <div
      class="absolute inset-0 z-0"
      :style="`background-image: url(${bgUrl}); background-size: cover; background-position: center;`"
    ></div>

    <!-- 遮罩層 -->
    <div class="absolute inset-0 bg-black bg-opacity-40 z-10"></div>

    <div class="relative z-10 flex flex-col items-center justify-center h-full px-4">
      <h1 class="text-3xl font-bold mb-2">社工專屬的訪視記錄助手</h1>
      <p class="text-lg mb-6">支援錄音上傳與逐字稿產出，AI自動生成訪視記錄，效率再升級。</p>

      <!-- 錄音中的狀態顯示 -->
      <div v-if="isRecording || isPaused" class="mb-4 p-4 bg-red-600 bg-opacity-80 rounded-lg">
        <div class="flex items-center justify-center gap-2 mb-2">
          <div
            class="w-3 h-3 rounded-full"
            :class="isPaused ? 'bg-yellow-300' : 'bg-red-300 animate-pulse'"
          ></div>
          <span class="text-white font-medium">
            {{ isPaused ? '錄音已暫停' : '錄音中...' }} {{ formatRecordingTime(recordingTime) }}
          </span>
        </div>

        <!-- 剩餘時間顯示 -->
        <div class="text-center mb-2">
          <span class="text-white text-sm">
            剩餘時間: {{ formatRemainingTime(remainingTime) }}
          </span>
        </div>

        <!-- 時間限制警告 -->
        <div
          v-if="isNearTimeLimit"
          class="text-center mb-3 text-yellow-300 text-sm flex items-center justify-center gap-1"
        >
          <i class="pi pi-exclamation-triangle"></i>
          <span>即將達到最大錄音時間 ({{ maxRecordingTimeMinutes }}分鐘)</span>
        </div>

        <!-- 進度條 -->
        <div class="w-full bg-red-800 rounded-full h-2 mb-3">
          <div
            class="h-2 rounded-full transition-all duration-1000"
            :class="isNearTimeLimit ? 'bg-yellow-300' : 'bg-white'"
            :style="{ width: (recordingTime / (maxRecordingTimeMinutes * 60)) * 100 + '%' }"
          ></div>
        </div>

        <div class="flex gap-3 justify-center">
          <!-- 暫停/繼續按鈕 -->
          <button
            v-if="isRecording"
            @click="pauseRecording"
            class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 font-medium flex items-center gap-2"
          >
            <i class="pi pi-pause"></i>
            暫停錄音
          </button>

          <button
            v-if="isPaused"
            @click="resumeRecording"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 font-medium flex items-center gap-2"
          >
            <i class="pi pi-play"></i>
            繼續錄音
          </button>

          <!-- 停止錄音按鈕 -->
          <button
            @click="stopRecording"
            class="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100 font-medium flex items-center gap-2"
          >
            <i class="pi pi-stop"></i>
            停止錄音
          </button>
        </div>
      </div>

      <!-- 按鈕區域 -->
      <div class="space-x-4 flex" v-if="!isRecording && !isPaused">
        <!-- 開始錄製按鈕 -->
        <button
          class="flex bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          @click="startRecording"
          :disabled="isProcessing || showingConfirm"
        >
          <img src="@/assets/voice.png" alt="record-icon" class="h-5 mr-1" />
          開始錄製
        </button>

        <!-- 上傳錄音檔按鈕 -->
        <input
          type="file"
          accept="audio/*"
          class="hidden"
          ref="audioInput"
          @change="handleAudioUpload"
        />
        <button
          class="flex bg-purple-700 text-white px-4 py-2 rounded hover:bg-purple-800"
          @click="triggerAudioInput"
          :disabled="isProcessing || showingConfirm"
        >
          <img src="@/assets/microphone.png" alt="upload-icon" class="h-5 mr-1" />
          上傳錄音檔
        </button>

        <!-- 上傳逐字稿按鈕 -->
        <input
          type="file"
          accept=".txt"
          class="hidden"
          ref="textInput"
          @change="handleTranscriptUpload"
        />
        <button
          class="flex bg-gray-50 text-purple-700 px-4 py-2 rounded border border-purple-700 hover:bg-gray-300"
          @click="triggerTextInput"
          :disabled="isProcessing || showingConfirm"
        >
          <img src="@/assets/document.png" alt="document-icon" class="h-5 mr-1" />
          上傳逐字稿
        </button>
      </div>

      <!-- 處理中的提示 -->
      <div v-if="isProcessing" class="mt-4 text-yellow-300 flex items-center gap-2">
        <i class="pi pi-spin pi-spinner"></i>
        <span>處理中...</span>
      </div>

      <!-- 錯誤提示 -->
      <div v-if="errorMessage" class="mt-4 p-3 bg-red-500 bg-opacity-80 rounded-lg">
        <div class="flex items-center gap-2 text-white">
          <i class="pi pi-exclamation-triangle"></i>
          <span v-html="errorMessage"></span>
        </div>
      </div>
    </div>

    <!-- 🔑 自定義確認對話框 - 避免重複 -->
    <div
      v-if="showingConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-xl max-w-md mx-4">
        <div class="flex items-center gap-3 mb-4">
          <i class="pi pi-exclamation-triangle text-orange-500 text-xl"></i>
          <h3 class="text-lg font-semibold text-gray-800">{{ confirmData.header }}</h3>
        </div>

        <div class="text-gray-600 mb-6 whitespace-pre-line leading-relaxed">
          {{ confirmData.message }}
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="cancelConfirm"
            class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
          >
            取消
          </button>
          <button
            @click="acceptConfirm"
            class="px-4 py-2 text-white bg-red-500 hover:bg-red-600 rounded transition-colors"
          >
            確定清除
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useRecording } from '@/composables/useRecording'
import { useFileUpload } from '@/composables/useFileUpload'
import bgUrl from '@/assets/banner-background-img.png'

// Emit events
const emit = defineEmits<{
  (event: 'audioUploaded', data: { file: File; url: string }): void
  (event: 'transcriptUploaded', data: { content: string }): void
  (event: 'recordingCompleted', data: { file: File; url: string }): void
}>()

// Store and composables
const store = useProjectStore()

const {
  isRecording,
  isPaused,
  recordingTime,
  startRecording: startRecordingComposable,
  pauseRecording: pauseRecordingComposable,
  resumeRecording: resumeRecordingComposable,
  stopRecording: stopRecordingComposable,
  formatRecordingTime,
  remainingTime,
  formatRemainingTime,
  isNearTimeLimit,
  maxRecordingTimeMinutes
} = useRecording()

const {
  isProcessing,
  handleAudioUpload: handleAudioUploadComposable,
  handleTranscriptUpload: handleTranscriptUploadComposable
} = useFileUpload()

// Refs
const audioInput = ref<HTMLInputElement | null>(null)
const textInput = ref<HTMLInputElement | null>(null)
const errorMessage = ref<string>('')

// 🔑 自定義確認對話框狀態
const showingConfirm = ref<boolean>(false)
const confirmData = ref<{
  header: string
  message: string
  callback: () => void
}>({
  header: '',
  message: '',
  callback: () => {}
})

// 文件大小限制 (100MB)
const MAX_FILE_SIZE = 100 * 1024 * 1024

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 檢查是否有需要保存的工作內容
const hasWorkToSave = computed(() => {
  return store.transcript.trim() || store.reportDraft.trim() || store.treatmentPlan.trim()
})

// 獲取需要保存的內容摘要
const getWorkSummary = (): string => {
  const items: string[] = []

  if (store.transcript.trim()) {
    items.push(`• 逐字稿 (${store.transcript.length} 字)`)
  }

  if (store.reportDraft.trim()) {
    items.push(`• 訪視記錄初稿 (${store.reportDraft.length} 字)`)
  }

  if (store.treatmentPlan.trim()) {
    items.push(`• 處遇計畫 (${store.treatmentPlan.length} 字)`)
  }

  return items.join('\n')
}

// 重置工作區內容
const resetWorkspace = () => {
  store.transcript = ''
  store.socialWorkerNotes = ''
  store.reportDraft = ''
  store.treatmentPlan = ''
  store.transcriptStatus = 'idle'
  store.transcriptProgress = 0
  store.reportStatus = 'idle'
  store.reportProgress = 0
  store.treatmentStatus = 'idle'
  store.treatmentProgress = 0
  store.reportConfig.selectedSections = []
  store.treatmentConfig.selectedServiceDomains = []
}

// 🔑 顯示自定義確認對話框
const showCustomConfirm = (actionType: string, callback: () => void): void => {
  if (!hasWorkToSave.value) {
    // 沒有工作內容，直接執行
    callback()
    return
  }

  let message = ''
  let header = ''

  switch (actionType) {
    case 'recording':
      header = '開始新錄音'
      break
    case 'upload-audio':
      header = '上傳新音檔'
      break
    case 'upload-transcript':
      header = '上傳新逐字稿'
      break
  }

  message = `目前工作區有以下內容將會被清除：\n\n${getWorkSummary()}\n\n建議先下載保存這些內容，確定要繼續嗎？`

  confirmData.value = {
    header,
    message,
    callback
  }

  showingConfirm.value = true
}

// 🔑 確認對話框操作
const acceptConfirm = () => {
  showingConfirm.value = false
  resetWorkspace()
  confirmData.value.callback()
}

const cancelConfirm = () => {
  showingConfirm.value = false
  confirmData.value = { header: '', message: '', callback: () => {} }
}

// 🔑 按鈕點擊處理函數
const startRecording = () => {
  showCustomConfirm('recording', async () => {
    try {
      errorMessage.value = ''
      await startRecordingComposable()
    } catch (error) {
      console.error('開始錄音失敗:', error)
      errorMessage.value = error instanceof Error ? error.message : '開始錄音失敗'
    }
  })
}

const triggerAudioInput = () => {
  showCustomConfirm('upload-audio', () => {
    errorMessage.value = ''
    audioInput.value?.click()
  })
}

const triggerTextInput = () => {
  showCustomConfirm('upload-transcript', () => {
    errorMessage.value = ''
    textInput.value?.click()
  })
}

// 其他不變的方法
const pauseRecording = () => {
  try {
    pauseRecordingComposable()
  } catch (error) {
    console.error('暫停錄音失敗:', error)
    errorMessage.value = '暫停錄音失敗'
  }
}

const resumeRecording = () => {
  try {
    resumeRecordingComposable()
  } catch (error) {
    console.error('恢復錄音失敗:', error)
    errorMessage.value = '恢復錄音失敗'
  }
}

const stopRecording = () => {
  try {
    stopRecordingComposable()
    // 錄音完成後發送事件
    if (store.audioFile && store.audioUrl) {
      emit('recordingCompleted', {
        file: store.audioFile,
        url: store.audioUrl
      })
    }
  } catch (error) {
    console.error('停止錄音失敗:', error)
    errorMessage.value = '停止錄音失敗'
  }
}

// 文件上傳處理
const handleAudioUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  try {
    errorMessage.value = ''

    // 檢查文件大小
    if (file.size > MAX_FILE_SIZE) {
      const fileSize = formatFileSize(file.size)
      const maxSize = formatFileSize(MAX_FILE_SIZE)

      errorMessage.value = `檔案過大！您上傳的檔案為 ${fileSize}，我們只支援 ${maxSize} 以下的檔案。請壓縮檔案或分段上傳。可到以下網站壓縮音訊：<a href="https://www.arkthinker.com/zh_tw/audio-compressor/" target="_blank">Arkthinker音訊壓縮工具</a>`

      if (audioInput.value) {
        audioInput.value.value = ''
      }
      return
    }

    const result = await handleAudioUploadComposable(file)
    emit('audioUploaded', result)

    if (audioInput.value) {
      audioInput.value.value = ''
    }
  } catch (error) {
    console.error('音檔上傳失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : '音檔上傳失敗'

    if (audioInput.value) {
      audioInput.value.value = ''
    }
  }
}

const handleTranscriptUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  try {
    errorMessage.value = ''
    const result = await handleTranscriptUploadComposable(file)
    emit('transcriptUploaded', result)

    if (textInput.value) {
      textInput.value.value = ''
    }
  } catch (error) {
    console.error('逐字稿上傳失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : '逐字稿上傳失敗'

    if (textInput.value) {
      textInput.value.value = ''
    }
  }
}
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button:disabled:hover {
  transform: none;
}

button:not(:disabled):hover {
  transform: translateY(-1px);
  transition: transform 0.2s ease;
}

.error-message {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
