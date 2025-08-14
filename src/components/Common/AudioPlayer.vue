<!-- File: components/Common/AudioPlayer.vue -->
<template>
  <div class="audio-player bg-gray-50 rounded-lg p-3 sm:p-4">
    <!-- 主要控制區域 -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 lg:gap-4 mb-3">
      <!-- 左側：播放控制和時間 -->
      <div class="flex items-center justify-between sm:justify-start gap-3">
        <!-- 播放控制按鈕 -->
        <div class="flex items-center gap-1 sm:gap-2">
          <Button
            :icon="isPlaying ? 'pi pi-pause' : 'pi pi-play'"
            @click="togglePlay"
            :rounded="true"
            size="small"
            :severity="isPlaying ? 'secondary' : 'primary'"
            :disabled="!isAudioReady"
            class="w-8 h-8 sm:w-10 sm:h-10"
          />
          <Button
            icon="pi pi-stop"
            @click="stop"
            :rounded="true"
            outlined
            size="small"
            :disabled="!isAudioReady"
            class="w-8 h-8 sm:w-10 sm:h-10"
          />
          <Button
            icon="pi pi-download"
            @click="downloadAudio"
            :rounded="true"
            outlined
            size="small"
            severity="success"
            v-tooltip.top="'下載音檔'"
            :disabled="!src"
            class="w-8 h-8 sm:w-10 sm:h-10"
          />
        </div>

        <!-- 時間顯示 -->
        <div class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-gray-600 font-mono">
          <span>{{ formatTime(currentTime) }}</span>
          <span>/</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- 右側：音量控制 -->
      <div class="flex items-center justify-center lg:justify-end gap-2 sm:gap-3">
        <Button
          :icon="isMuted ? 'pi pi-volume-off' : 'pi pi-volume-up'"
          @click="toggleMute"
          :rounded="true"
          outlined
          size="small"
          :disabled="!isAudioReady"
          class="w-8 h-8 sm:w-10 sm:h-10"
        />
        <div class="flex items-center gap-1 sm:gap-2">
          <span class="text-xs text-gray-500 w-6 sm:w-8 text-center">{{ volume }}%</span>
          <div class="w-16 sm:w-20">
            <input
              type="range"
              min="0"
              max="100"
              v-model="volume"
              @input="updateVolume"
              class="volume-slider w-full"
              :disabled="!isAudioReady"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 進度條區域 -->
    <div class="mb-3">
      <div
        class="w-full bg-gray-300 rounded-full h-2 cursor-pointer relative overflow-hidden"
        :class="{ 'cursor-not-allowed': !isAudioReady }"
        @click="seek"
        ref="progressBar"
      >
        <div
          class="bg-blue-600 h-full rounded-full transition-all duration-200 ease-out"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>

    <!-- 檔案資訊和狀態 -->
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 sm:gap-0">
      <div class="flex items-center gap-2 text-gray-600 min-w-0">
        <i class="pi pi-file-audio text-xs sm:text-sm flex-shrink-0"></i>
        <span class="truncate text-xs sm:text-sm" :title="filename || '音檔'">
          {{ filename || '音檔' }}
        </span>
      </div>

      <!-- 狀態指示器 -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <div v-if="isLoading" class="flex items-center gap-1 text-blue-600">
          <i class="pi pi-spin pi-spinner text-xs"></i>
          <span class="text-xs">載入中</span>
        </div>
        <div v-else-if="hasError" class="flex items-center gap-1 text-red-600 text-xs">
          <i class="pi pi-exclamation-triangle"></i>
          <span class="hidden sm:inline">載入失敗</span>
          <span class="sm:hidden">失敗</span>
        </div>
        <div v-else-if="isAudioReady" class="flex items-center gap-1 text-green-600 text-xs">
          <i class="pi pi-check-circle"></i>
          <span class="hidden sm:inline">就緒</span>
          <span class="sm:hidden">✓</span>
        </div>
      </div>
    </div>

    <!-- 隱藏的 audio 元素 -->
    <audio
      ref="audioElement"
      :src="src"
      @loadstart="onLoadStart"
      @loadeddata="onLoadedData"
      @loadedmetadata="onLoadedMetadata"
      @canplay="onCanPlay"
      @canplaythrough="onCanPlayThrough"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @error="onError"
      @durationchange="onDurationChange"
      preload="metadata"
      crossorigin="anonymous"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Button from 'primevue/button'

interface Props {
  src: string
  filename?: string
}

const props = defineProps<Props>()

const audioElement = ref<HTMLAudioElement | null>(null)
const progressBar = ref<HTMLDivElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(50)
const isMuted = ref(false)
const isAudioReady = ref(false)
const hasError = ref(false)
const isLoading = ref(false)

// Computed
const progress = computed(() => {
  if (duration.value === 0 || !isFinite(duration.value)) return 0
  return Math.min(100, (currentTime.value / duration.value) * 100)
})

// Methods

// 更新音量
const updateVolume = () => {
  if (audioElement.value) {
    // 將百分比轉換為 0-1 的範圍
    audioElement.value.volume = volume.value / 100

    // 可選：保存音量設定到 localStorage
    localStorage.setItem('audio-player-volume', volume.value.toString())

    console.log(`音量已調整為: ${volume.value}%`)
  }
}

const formatTime = (time: number): string => {
  if (!isFinite(time) || isNaN(time) || time < 0) return '00:00'
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

const togglePlay = async () => {
  if (!audioElement.value || !isAudioReady.value) return

  try {
    if (isPlaying.value) {
      audioElement.value.pause()
    } else {
      await audioElement.value.play()
    }
  } catch (error) {
    console.error('播放失敗:', error)
    hasError.value = true
  }
}

const stop = () => {
  if (!audioElement.value) return

  audioElement.value.pause()
  audioElement.value.currentTime = 0
  isPlaying.value = false
}

const seek = (event: MouseEvent) => {
  if (!audioElement.value || !progressBar.value || !isAudioReady.value) return
  if (!isFinite(duration.value) || duration.value === 0) return

  const rect = progressBar.value.getBoundingClientRect()
  const percent = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width))
  const newTime = percent * duration.value

  if (isFinite(newTime) && newTime >= 0) {
    audioElement.value.currentTime = newTime
  }
}

const toggleMute = () => {
  if (!audioElement.value) return

  isMuted.value = !isMuted.value
  audioElement.value.muted = isMuted.value
}

// 下載音檔
const downloadAudio = async () => {
  if (!props.src) return

  try {
    // 獲取檔案名稱和副檔名
    const fileName = props.filename || 'audio'
    const fileExtension = getFileExtension(fileName) || 'wav'
    const downloadFileName = fileName.includes('.') ? fileName : `${fileName}.${fileExtension}`

    // 如果是 blob URL，直接下載
    if (props.src.startsWith('blob:')) {
      const link = document.createElement('a')
      link.href = props.src
      link.download = downloadFileName
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else {
      // 如果是普通 URL，fetch 後下載
      const response = await fetch(props.src)
      if (!response.ok) {
        throw new Error('下載失敗')
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      const link = document.createElement('a')
      link.href = url
      link.download = downloadFileName
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // 清理 URL
      setTimeout(() => URL.revokeObjectURL(url), 100)
    }

    console.log('音檔下載成功:', downloadFileName)
  } catch (error) {
    console.error('下載音檔失敗:', error)
    // 可以在這裡添加錯誤提示
  }
}

// 獲取檔案副檔名
const getFileExtension = (filename: string): string => {
  const lastDotIndex = filename.lastIndexOf('.')
  if (lastDotIndex === -1 || lastDotIndex === filename.length - 1) {
    return ''
  }
  return filename.substring(lastDotIndex + 1).toLowerCase()
}

// 強制載入音檔並獲取時長
const forceLoadDuration = async () => {
  if (!audioElement.value) return

  try {
    // 對於錄音檔案，嘗試播放一小段來獲取時長
    const originalVolume = audioElement.value.volume
    const originalMuted = audioElement.value.muted

    audioElement.value.volume = 0
    audioElement.value.muted = true

    await audioElement.value.play()

    // 等待一小段時間讓瀏覽器計算時長
    setTimeout(() => {
      if (audioElement.value) {
        audioElement.value.pause()
        audioElement.value.currentTime = 0
        audioElement.value.volume = originalVolume
        audioElement.value.muted = originalMuted

        // 檢查是否獲得了有效的時長
        if (isFinite(audioElement.value.duration) && audioElement.value.duration > 0) {
          duration.value = audioElement.value.duration
          isAudioReady.value = true
          isLoading.value = false
        }
      }
    }, 100)
  } catch (error) {
    console.log('Force load failed, trying alternative method')
    // 如果播放失敗，嘗試其他方法
    tryAlternativeLoadMethod()
  }
}

// 嘗試替代載入方法
const tryAlternativeLoadMethod = () => {
  if (!audioElement.value) return

  // 監聽時間更新來獲取時長
  let timeUpdateCount = 0
  const timeUpdateHandler = () => {
    if (audioElement.value && isFinite(audioElement.value.duration)) {
      duration.value = audioElement.value.duration
      isAudioReady.value = true
      isLoading.value = false
      audioElement.value.removeEventListener('timeupdate', timeUpdateHandler)
    } else {
      timeUpdateCount++
      // 如果嘗試多次仍無法獲得時長，設置為就緒狀態
      if (timeUpdateCount > 10) {
        isAudioReady.value = true
        isLoading.value = false
        audioElement.value?.removeEventListener('timeupdate', timeUpdateHandler)
      }
    }
  }

  audioElement.value.addEventListener('timeupdate', timeUpdateHandler)

  // 嘗試設置 currentTime 來觸發載入
  setTimeout(() => {
    if (audioElement.value) {
      audioElement.value.currentTime = 0.1
      setTimeout(() => {
        if (audioElement.value) {
          audioElement.value.currentTime = 0
        }
      }, 50)
    }
  }, 100)
}

// Event handlers
const onLoadStart = () => {
  isLoading.value = true
  hasError.value = false
  isAudioReady.value = false
  duration.value = 0
}

const onLoadedData = () => {
  console.log('Audio data loaded')
}

const onLoadedMetadata = () => {
  if (audioElement.value) {
    const audioDuration = audioElement.value.duration
    if (isFinite(audioDuration) && audioDuration > 0) {
      duration.value = audioDuration
      isAudioReady.value = true
      isLoading.value = false
      console.log('Audio duration loaded:', audioDuration)
    } else {
      console.log('Duration not available in metadata, trying force load')
      forceLoadDuration()
    }
  }
}

const onCanPlay = () => {
  if (!isAudioReady.value && isFinite(audioElement.value?.duration || 0)) {
    duration.value = audioElement.value?.duration || 0
    isAudioReady.value = true
    isLoading.value = false
  }
}

const onCanPlayThrough = () => {
  if (!isAudioReady.value) {
    duration.value = audioElement.value?.duration || 0
    isAudioReady.value = true
    isLoading.value = false
  }
}

const onDurationChange = () => {
  if (audioElement.value && isFinite(audioElement.value.duration)) {
    duration.value = audioElement.value.duration
    if (!isAudioReady.value) {
      isAudioReady.value = true
      isLoading.value = false
    }
  }
}

const onTimeUpdate = () => {
  if (audioElement.value) {
    const time = audioElement.value.currentTime
    if (isFinite(time)) {
      currentTime.value = time
    }

    // 如果還沒有時長，嘗試獲取
    if (!isFinite(duration.value) && isFinite(audioElement.value.duration)) {
      duration.value = audioElement.value.duration
      if (!isAudioReady.value) {
        isAudioReady.value = true
        isLoading.value = false
      }
    }
  }
}

const onEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
}

const onError = (event: Event) => {
  console.error('Audio error:', event)
  hasError.value = true
  isAudioReady.value = false
  isLoading.value = false
}

// 重新載入音檔
const reloadAudio = async () => {
  if (!audioElement.value) return

  isAudioReady.value = false
  hasError.value = false
  isLoading.value = true
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0

  try {
    audioElement.value.load()

    // 等待載入並嘗試獲取時長
    setTimeout(() => {
      if (audioElement.value && !isFinite(audioElement.value.duration)) {
        forceLoadDuration()
      }
    }, 200)
  } catch (error) {
    console.error('Reload audio failed:', error)
    hasError.value = true
    isLoading.value = false
  }
}

// Watch for src changes
watch(
  () => props.src,
  async () => {
    if (props.src) {
      await reloadAudio()
    }
  },
  { immediate: true }
)

// Lifecycle
onMounted(() => {
  if (audioElement.value) {
    audioElement.value.volume = volume.value / 100

    audioElement.value.addEventListener('play', () => {
      isPlaying.value = true
    })

    audioElement.value.addEventListener('pause', () => {
      isPlaying.value = false
    })
  }
})

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.removeEventListener('play', () => {})
    audioElement.value.removeEventListener('pause', () => {})
  }
})
</script>

<style scoped>
/* 自定義音量滑條樣式 */
.volume-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #d1d5db;
  outline: none;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.volume-slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.volume-slider::-moz-range-track {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #d1d5db;
  border: none;
}

.volume-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #3b82f6;
  border: none;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.volume-slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.volume-slider:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.volume-slider:disabled::-webkit-slider-thumb {
  cursor: not-allowed;
}

.volume-slider:disabled::-moz-range-thumb {
  cursor: not-allowed;
}

/* 禁用狀態樣式 */
.cursor-not-allowed {
  cursor: not-allowed;
}

/* 載入動畫 */
.pi-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 文字截斷 */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 等寬字體讓時間顯示更整齊 */
.font-mono {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Monaco, Consolas, 'Liberation Mono',
    'Courier New', monospace;
}

/* 音量滑桿樣式優化 */
.volume-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  background: #d1d5db;
  border-radius: 5px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

.volume-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

/* 手機版按鈕微調 */
@media (max-width: 640px) {
  :deep(.p-button) {
    padding: 0.25rem;
  }

  :deep(.p-button-icon) {
    font-size: 0.875rem;
  }
}

/* 確保在極小螢幕上也能正常顯示 */
@media (max-width: 480px) {
  .volume-slider::-webkit-slider-thumb {
    width: 14px;
    height: 14px;
  }

  .volume-slider::-moz-range-thumb {
    width: 14px;
    height: 14px;
  }
}
</style>
