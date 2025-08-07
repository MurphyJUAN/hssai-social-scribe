import { ref, computed } from 'vue'
import { apiService } from '@/services/apiService'

export interface VoiceInputOptions {
  maxDurationMinutes?: number
  maxFileSizeMB?: number
  onProgress?: (progress: number) => void
  onTranscript?: (text: string) => void
}

export function useVoiceInput(options: VoiceInputOptions = {}) {
  const {
    maxDurationMinutes = 10, // 最大10分鐘
    maxFileSizeMB = 80, // 預留20MB緩衝
    onProgress = () => {},
    onTranscript = () => {}
  } = options

  // 狀態管理
  const isRecording = ref(false)
  const isPaused = ref(false)
  const isTranscribing = ref(false)
  const recordingTime = ref(0)
  const transcriptProgress = ref(0)
  const error = ref<string | null>(null)

  // MediaRecorder 相關
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])
  const recordingInterval = ref<number | null>(null)

  // 計算屬性
  const canRecord = computed(() => !isRecording.value && !isTranscribing.value)
  const canPause = computed(() => isRecording.value && !isPaused.value)
  const canResume = computed(() => isRecording.value && isPaused.value)
  const canStop = computed(() => isRecording.value)

  const maxDurationMs = computed(() => maxDurationMinutes * 60 * 1000)
  const recordingTimeFormatted = computed(() => {
    const minutes = Math.floor(recordingTime.value / 60000)
    const seconds = Math.floor((recordingTime.value % 60000) / 1000)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })

  const remainingTime = computed(() => {
    const remaining = maxDurationMs.value - recordingTime.value
    const minutes = Math.floor(remaining / 60000)
    const seconds = Math.floor((remaining % 60000) / 1000)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })

  const isNearTimeLimit = computed(() => {
    return recordingTime.value > maxDurationMs.value * 0.9 // 90% 時間時警告
  })

  // 開始錄音
  const startRecording = async (): Promise<void> => {
    try {
      error.value = null
      audioChunks.value = []
      recordingTime.value = 0

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      })

      mediaRecorder.value = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      mediaRecorder.value.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        await processRecording()
      }

      mediaRecorder.value.start(1000) // 每秒收集一次數據
      isRecording.value = true

      // 開始計時
      recordingInterval.value = window.setInterval(() => {
        recordingTime.value += 1000

        // 檢查是否達到最大時長
        if (recordingTime.value >= maxDurationMs.value) {
          stopRecording()
        }
      }, 1000)
    } catch (err) {
      error.value = '無法訪問麥克風，請檢查權限設置'
      console.error('Recording error:', err)
    }
  }

  // 暫停錄音
  const pauseRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
      mediaRecorder.value.pause()
      isPaused.value = true

      if (recordingInterval.value) {
        clearInterval(recordingInterval.value)
      }
    }
  }

  // 恢復錄音
  const resumeRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state === 'paused') {
      mediaRecorder.value.resume()
      isPaused.value = false

      // 重新開始計時
      recordingInterval.value = window.setInterval(() => {
        recordingTime.value += 1000

        if (recordingTime.value >= maxDurationMs.value) {
          stopRecording()
        }
      }, 1000)
    }
  }

  // 停止錄音
  const stopRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop()
    }

    isRecording.value = false
    isPaused.value = false

    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
      recordingInterval.value = null
    }
  }

  // 取消錄音
  const cancelRecording = (): void => {
    stopRecording()
    audioChunks.value = []
    recordingTime.value = 0
    error.value = null
  }

  // 處理錄音 - 轉換為文字
  const processRecording = async (): Promise<void> => {
    try {
      if (audioChunks.value.length === 0) {
        throw new Error('沒有錄音數據')
      }

      isTranscribing.value = true
      transcriptProgress.value = 0
      error.value = null

      // 創建音頻 Blob
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })

      // 檢查文件大小
      const fileSizeMB = audioBlob.size / (1024 * 1024)
      if (fileSizeMB > maxFileSizeMB) {
        throw new Error(`錄音檔案過大 (${fileSizeMB.toFixed(1)}MB)，請錄製更短的音頻`)
      }

      // 創建 File 對象
      const audioFile = new File([audioBlob], `voice_input_${Date.now()}.webm`, {
        type: 'audio/webm'
      })

      // 調用轉錄 API
      const transcript = await apiService.transcribeAudio(audioFile, (progress: number) => {
        transcriptProgress.value = progress
        onProgress(progress)
      })

      // 回調轉錄結果
      onTranscript(transcript)

      // 清理
      audioChunks.value = []
      recordingTime.value = 0
    } catch (err) {
      error.value = err instanceof Error ? err.message : '轉錄失敗'
      console.error('Transcription error:', err)
    } finally {
      isTranscribing.value = false
      transcriptProgress.value = 0
    }
  }

  // 檢查瀏覽器支持
  const isSupported = computed(() => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder)
  })

  // 清理資源
  const cleanup = (): void => {
    if (isRecording.value) {
      cancelRecording()
    }

    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
    }
  }

  return {
    // 狀態
    isRecording,
    isPaused,
    isTranscribing,
    recordingTime,
    transcriptProgress,
    error,

    // 計算屬性
    canRecord,
    canPause,
    canResume,
    canStop,
    recordingTimeFormatted,
    remainingTime,
    isNearTimeLimit,
    isSupported,

    // 方法
    startRecording,
    pauseRecording,
    resumeRecording,
    stopRecording,
    cancelRecording,
    cleanup
  }
}
