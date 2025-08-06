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
        <div class="flex items-center justify-center gap-2 mb-3">
          <div
            class="w-3 h-3 rounded-full"
            :class="isPaused ? 'bg-yellow-300' : 'bg-red-300 animate-pulse'"
          ></div>
          <span class="text-white font-medium">
            {{ isPaused ? '錄音已暫停' : '錄音中...' }} {{ formatRecordingTime(recordingTime) }}
          </span>
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
          :disabled="isProcessing"
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
          :disabled="isProcessing"
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
          :disabled="isProcessing"
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
          <span>{{ errorMessage }}</span>
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
  formatRecordingTime
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

// Methods
const startRecording = async () => {
  try {
    errorMessage.value = ''
    await startRecordingComposable()
  } catch (error) {
    console.error('開始錄音失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : '開始錄音失敗'
  }
}

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

const triggerAudioInput = () => {
  errorMessage.value = ''
  audioInput.value?.click()
}

const triggerTextInput = () => {
  errorMessage.value = ''
  textInput.value?.click()
}

const handleAudioUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  try {
    errorMessage.value = ''
    const result = await handleAudioUploadComposable(file)
    emit('audioUploaded', result)

    // 清空 input
    if (audioInput.value) {
      audioInput.value.value = ''
    }
  } catch (error) {
    console.error('音檔上傳失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : '音檔上傳失敗'

    // 清空 input
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

    // 清空 input
    if (textInput.value) {
      textInput.value.value = ''
    }
  } catch (error) {
    console.error('逐字稿上傳失敗:', error)
    errorMessage.value = error instanceof Error ? error.message : '逐字稿上傳失敗'

    // 清空 input
    if (textInput.value) {
      textInput.value.value = ''
    }
  }
}

// 清除錯誤訊息
const clearError = () => {
  errorMessage.value = ''
}

// 如果有錯誤訊息，5秒後自動清除
let errorTimer: number | null = null
const showError = (message: string) => {
  errorMessage.value = message

  if (errorTimer) {
    clearTimeout(errorTimer)
  }

  errorTimer = window.setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
}
</script>

<style scoped>
/* 可以加入一些自定義樣式 */
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

/* 按鈕 hover 效果 */
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

/* 錯誤訊息淡入動畫 */
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
