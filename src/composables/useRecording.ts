// composables/useRecording.ts
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/useProjectStore'

export function useRecording() {
  const projectStore = useProjectStore()

  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])
  const stream = ref<MediaStream | null>(null)

  // 🔑 新增：最大錄音時間（90分鐘 = 5400秒）
  const MAX_RECORDING_TIME = 90 * 60 // 5400秒

  const isRecording = computed(() => projectStore.isRecording)
  const isPaused = computed(() => projectStore.isPaused)
  const recordingTime = computed(() => projectStore.recordingTime)

  // 🔑 新增：剩餘時間計算
  const remainingTime = computed(() => {
    return Math.max(0, MAX_RECORDING_TIME - projectStore.recordingTime)
  })

  // 🔑 新增：是否接近時間限制
  const isNearTimeLimit = computed(() => {
    return projectStore.recordingTime > MAX_RECORDING_TIME * 0.9 // 90%時警告
  })

  let recordingTimer: number | null = null

  // 開始錄音
  const startRecording = async (): Promise<void> => {
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })

      // 選擇最佳的錄音格式
      const options: MediaRecorderOptions = {}
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options.mimeType = 'audio/webm;codecs=opus'
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options.mimeType = 'audio/webm'
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        options.mimeType = 'audio/mp4'
      } else if (MediaRecorder.isTypeSupported('audio/wav')) {
        options.mimeType = 'audio/wav'
      }

      mediaRecorder.value = new MediaRecorder(stream.value, options)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      mediaRecorder.value.onstop = () => {
        const mimeType = mediaRecorder.value?.mimeType || 'audio/wav'
        const fileExtension = getFileExtensionFromMimeType(mimeType)

        const audioBlob = new Blob(audioChunks.value, { type: mimeType })
        const audioFile = new File([audioBlob], `recording_${Date.now()}.${fileExtension}`, {
          type: mimeType,
          lastModified: Date.now()
        })
        const audioUrl = URL.createObjectURL(audioBlob)

        projectStore.setAudioFile(audioFile, audioUrl)
        stopTimer()
      }

      // 設定錄音片段間隔（每秒記錄一次）
      mediaRecorder.value.start(1000)
      projectStore.isRecording = true
      projectStore.recordingTime = 0
      startTimer()
    } catch (error) {
      console.error('無法開始錄音:', error)
      throw new Error('無法開始錄音，請檢查麥克風權限')
    }
  }

  // 根據 MIME 類型獲取檔案副檔名
  const getFileExtensionFromMimeType = (mimeType: string): string => {
    const typeMap: Record<string, string> = {
      'audio/webm': 'webm',
      'audio/webm;codecs=opus': 'webm',
      'audio/mp4': 'm4a',
      'audio/wav': 'wav',
      'audio/ogg': 'ogg'
    }
    return typeMap[mimeType] || 'wav'
  }

  // 暫停錄音
  const pauseRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
      mediaRecorder.value.pause()
      projectStore.isRecording = false
      projectStore.isPaused = true
      stopTimer()
    }
  }

  // 恢復錄音
  const resumeRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state === 'paused') {
      mediaRecorder.value.resume()
      projectStore.isRecording = true
      projectStore.isPaused = false
      startTimer()
    }
  }

  // 停止錄音
  const stopRecording = (): void => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop()

      if (stream.value) {
        stream.value.getTracks().forEach((track) => track.stop())
      }

      projectStore.isRecording = false
      projectStore.isPaused = false
      stopTimer()
    }
  }

  // 🔑 修改：計時器加入時間限制檢查
  const startTimer = (): void => {
    recordingTimer = window.setInterval(() => {
      projectStore.recordingTime++

      // 🔑 檢查是否達到最大錄音時間
      if (projectStore.recordingTime >= MAX_RECORDING_TIME) {
        console.log('⏰ 達到最大錄音時間（90分鐘），自動停止錄音')
        stopRecording()
      }
    }, 1000)
  }

  const stopTimer = (): void => {
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }

  // 格式化錄音時間
  const formatRecordingTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // 🔑 新增：格式化剩餘時間
  const formatRemainingTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return {
    isRecording,
    isPaused,
    recordingTime,
    startRecording,
    pauseRecording,
    resumeRecording,
    stopRecording,
    formatRecordingTime,
    // 🔑 新增的返回值
    remainingTime,
    formatRemainingTime,
    isNearTimeLimit,
    maxRecordingTimeMinutes: 90
  }
}
