<template>
  <div class="voice-input-container">
    <!-- 語音輸入按鈕 -->
    <div class="flex items-center gap-2">
      <Button
        v-if="!isRecording && !isTranscribing"
        @click="startRecording"
        :disabled="!isSupported || !canRecord"
        class="voice-input-btn"
        severity="secondary"
        outlined
      >
        <i class="pi pi-microphone mr-2"></i>
        語音輸入
      </Button>

      <!-- 錄音控制區域 -->
      <div
        v-if="isRecording"
        class="recording-controls flex items-center gap-2 p-3 border rounded-lg bg-red-50"
      >
        <div class="flex items-center gap-2">
          <div class="recording-indicator">
            <i class="pi pi-circle text-red-500 animate-pulse"></i>
          </div>

          <div class="recording-info">
            <div class="text-sm font-medium">
              {{ recordingTimeFormatted }}
            </div>
            <div class="text-xs text-gray-500">剩餘 {{ remainingTime }}</div>
          </div>
        </div>

        <div class="flex gap-2">
          <!-- 暫停/恢復按鈕 -->
          <Button
            v-if="!isPaused"
            @click="pauseRecording"
            size="small"
            severity="secondary"
            outlined
          >
            <i class="pi pi-pause"></i>
          </Button>

          <Button v-else @click="resumeRecording" size="small" severity="success" outlined>
            <i class="pi pi-play"></i>
          </Button>

          <!-- 停止按鈕 -->
          <Button @click="stopRecording" size="small" severity="success">
            <i class="pi pi-stop mr-1"></i>
            完成
          </Button>

          <!-- 取消按鈕 -->
          <Button @click="cancelRecording" size="small" severity="danger" outlined>
            <i class="pi pi-times"></i>
          </Button>
        </div>
      </div>

      <!-- 轉錄進度 -->
      <div
        v-if="isTranscribing"
        class="transcribing-status flex items-center gap-2 p-3 border rounded-lg bg-blue-50"
      >
        <i class="pi pi-spin pi-spinner text-blue-600"></i>
        <div>
          <div class="text-sm font-medium">正在轉換語音...</div>
          <div class="text-xs text-gray-500">{{ transcriptProgress }}%</div>
        </div>
      </div>
    </div>

    <!-- 時間限制警告 -->
    <div
      v-if="isRecording && isNearTimeLimit"
      class="time-warning mt-2 p-2 bg-orange-100 border border-orange-300 rounded text-sm text-orange-700"
    >
      <i class="pi pi-exclamation-triangle mr-1"></i>
      錄音即將達到時間限制 ({{ maxDurationMinutes }} 分鐘)
    </div>

    <!-- 錯誤提示 -->
    <Message v-if="error" severity="error" :closable="false" class="mt-2">
      {{ error }}
    </Message>

    <!-- 使用提示 -->
    <div v-if="!isSupported" class="mt-2 p-2 bg-gray-100 border rounded text-sm text-gray-600">
      <i class="pi pi-info-circle mr-1"></i>
      您的瀏覽器不支援語音輸入功能
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted } from 'vue'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useVoiceInput } from '@/composables/useVoiceInput'

interface Props {
  maxDurationMinutes?: number
  maxFileSizeMB?: number
}

interface Emits {
  (e: 'transcript', text: string): void
  (e: 'progress', progress: number): void
  (e: 'error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  maxDurationMinutes: 10,
  maxFileSizeMB: 80
})

const emit = defineEmits<Emits>()

// 使用語音輸入 composable
const {
  isRecording,
  isPaused,
  isTranscribing,
  recordingTime,
  transcriptProgress,
  error,
  canRecord,
  canPause,
  canResume,
  canStop,
  recordingTimeFormatted,
  remainingTime,
  isNearTimeLimit,
  isSupported,
  startRecording,
  pauseRecording,
  resumeRecording,
  stopRecording,
  cancelRecording,
  cleanup
} = useVoiceInput({
  maxDurationMinutes: props.maxDurationMinutes,
  maxFileSizeMB: props.maxFileSizeMB,
  onProgress: (progress: number) => emit('progress', progress),
  onTranscript: (text: string) => emit('transcript', text)
})

// 當組件銷毀時清理資源
onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.voice-input-btn {
  transition: all 0.3s ease;
}

.voice-input-btn:hover {
  transform: translateY(-1px);
}

.recording-indicator {
  animation: pulse 1.5s infinite;
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

.recording-controls {
  border: 2px solid #ef4444;
  animation: glow 2s infinite;
}

@keyframes glow {
  0%,
  100% {
    box-shadow: 0 0 5px rgba(239, 68, 68, 0.3);
  }
  50% {
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
  }
}
</style>
