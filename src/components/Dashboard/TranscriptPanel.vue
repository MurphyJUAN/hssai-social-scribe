<template>
  <div class="transcript-panel space-y-6">
    <!-- 音檔播放器區域 (只有上傳音檔時顯示) -->
    <Card v-if="audioUrl" class="player-card">
      <template #title>
        <div class="flex items-center gap-2">
          <i class="pi pi-volume-up text-purple-600"></i>
          錄音檔案
        </div>
      </template>
      <template #content>
        <AudioPlayer :src="audioUrl" :filename="audioFileName" />
      </template>
    </Card>

    <!-- 逐字稿區域 -->
    <Card class="transcript-card">
      <template #title>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="pi pi-file-text text-blue-600"></i>
            逐字稿內容
          </div>
          <div
            v-if="transcriptStatus === 'processing'"
            class="flex items-center gap-2 text-sm text-blue-600"
          >
            <i class="pi pi-spin pi-spinner"></i>
            AI 轉換中... {{ transcriptProgress }}%
          </div>
        </div>
      </template>
      <template #content>
        <div class="space-y-4">
          <!-- 轉換進度條 -->
          <ProgressBar
            v-if="transcriptStatus === 'processing'"
            :value="transcriptProgress"
            class="mb-4"
          />

          <!-- 逐字稿文字區域 -->
          <Textarea
            v-model="transcript"
            placeholder="逐字稿內容將在此顯示，或您可以直接上傳逐字稿文件..."
            :rows="15"
            class="w-full resize-none"
            :disabled="transcriptStatus === 'processing'"
          />

          <!-- 文件上傳提示 -->
          <div
            v-if="!audioUrl && !transcript"
            class="text-center p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
          >
            <i class="pi pi-upload text-2xl text-gray-400 mb-2"></i>
            <p class="text-sm text-gray-600 mb-2">
              您可以直接在上方文本框輸入內容，或回到上方上傳逐字稿文件
            </p>
            <p class="text-xs text-gray-500">
              支援格式化的逐字稿文件（包含逐字稿內容和社工補充說明段落）
            </p>
          </div>

          <!-- 轉換按鈕 (如果有音檔但沒有逐字稿) -->
          <div v-if="audioUrl && !transcript.trim()" class="text-center">
            <Button
              label="開始轉換逐字稿"
              icon="pi pi-play"
              @click="startTranscription"
              :loading="transcriptStatus === 'processing'"
              class="bg-blue-500 hover:bg-blue-600"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- 社工補充說明 -->
    <Card class="notes-card">
      <template #title>
        <div class="flex items-center gap-2">
          <i class="pi pi-pencil text-green-600"></i>
          其他補充說明
          <div v-if="socialWorkerNotes.trim()" class="ml-2">
            <Badge :value="`${socialWorkerNotes.length} 字`" severity="info" />
          </div>
        </div>
      </template>
      <template #content>
        <div class="space-y-3">
          <!-- 語音輸入組件 -->
          <VoiceInput
            :max-duration-minutes="10"
            :max-file-size-mb="80"
            @transcript="handleVoiceTranscript"
            @progress="handleVoiceProgress"
            @error="handleVoiceError"
          />

          <!-- 文字輸入區域 -->
          <Textarea
            v-model="socialWorkerNotes"
            placeholder="請在此補充相關說明、觀察重點或其他需要記錄的資訊... (可使用上方語音輸入功能，或從逐字稿文件自動解析)"
            :rows="8"
            class="w-full resize-none"
          />

          <!-- 補充說明提示 -->
          <div
            v-if="!socialWorkerNotes.trim()"
            class="text-xs text-gray-500 flex items-center gap-1"
          >
            <i class="pi pi-info-circle"></i>
            <span>您可以直接輸入、使用語音輸入，或上傳包含補充說明的逐字稿文件</span>
          </div>
        </div>
      </template>
    </Card>

    <!-- 操作按鈕區域 -->
    <div class="flex justify-between items-center pt-4 border-t">
      <div class="text-sm text-gray-500">
        <span v-if="canProceedToConfig" class="text-green-600 flex items-center gap-1">
          <i class="pi pi-check-circle"></i>
          逐字稿已完成，可以進入下一步
          <Badge
            v-if="transcript.length > 0"
            :value="`${transcript.length} 字`"
            severity="success"
            class="ml-2"
          />
        </span>
        <span v-else class="text-orange-600 flex items-center gap-1">
          <i class="pi pi-exclamation-triangle"></i>
          請等待逐字稿轉換完成或上傳逐字稿內容
        </span>
      </div>

      <div class="flex gap-3">
        <!-- 合併下載按鈕 -->
        <Button
          v-if="transcript.trim() || socialWorkerNotes.trim()"
          label="下載完整內容"
          icon="pi pi-download"
          @click="downloadCombinedContent"
          severity="secondary"
          outlined
        />

        <!-- 分別下載按鈕 -->
        <div v-if="transcript.trim() || socialWorkerNotes.trim()" class="relative">
          <Button
            icon="pi pi-chevron-down"
            severity="secondary"
            outlined
            @click="showDownloadMenu = !showDownloadMenu"
            class="p-button-sm"
          />

          <!-- 下載選單 -->
          <div
            v-if="showDownloadMenu"
            class="absolute right-0 top-full mt-1 bg-white border rounded-lg shadow-lg z-10 min-w-48"
          >
            <div class="py-1">
              <button
                v-if="transcript.trim()"
                @click="downloadTranscript"
                class="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
              >
                <i class="pi pi-file-text text-sm"></i>
                下載逐字稿
              </button>
              <button
                v-if="socialWorkerNotes.trim()"
                @click="downloadNotes"
                class="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
              >
                <i class="pi pi-pencil text-sm"></i>
                下載補充說明
              </button>
              <button
                v-if="transcript.trim() && socialWorkerNotes.trim()"
                @click="downloadCombinedContent"
                class="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
              >
                <i class="pi pi-download text-sm"></i>
                下載完整內容
              </button>
            </div>
          </div>
        </div>

        <Button
          label="下一步：記錄設定"
          icon="pi pi-arrow-right"
          @click="proceedToConfig"
          :disabled="!canProceedToConfig"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useSessionStore } from '@/stores/useSessionStore'
import { useApiIntegration } from '@/composables/useApiIntegration'
import { useDownload } from '@/composables/useDownload'
import { useToast } from 'primevue/usetoast'

// Components
import Card from 'primevue/card'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import ProgressBar from 'primevue/progressbar'
import AudioPlayer from '@/components/Common/AudioPlayer.vue'
import VoiceInput from '@/components/Common/VoiceInput.vue'

const projectStore = useProjectStore()
const sessionStore = useSessionStore()
const toast = useToast()
const { transcribeAudio } = useApiIntegration()
const { downloadTranscript: downloadTranscriptFile } = useDownload()

const {
  audioUrl,
  transcript,
  socialWorkerNotes,
  transcriptStatus,
  transcriptProgress,
  canProceedToConfig,
  audioFile
} = storeToRefs(projectStore)

onMounted(() => {
  console.log('=== TranscriptPanel onMounted ===')
  console.log('Store transcript:', projectStore.transcript)
  console.log('Store socialWorkerNotes:', projectStore.socialWorkerNotes)
  console.log('Ref transcript:', transcript.value)
  console.log('Ref socialWorkerNotes:', socialWorkerNotes.value)
})

// 本地狀態
const showDownloadMenu = ref(false)

// Computed
const audioFileName = computed(() => {
  return audioFile.value?.name || '未知檔案'
})

// Methods
const startTranscription = async () => {
  try {
    projectStore.setTranscriptStatus('processing', 0)

    // 🔑 立即顯示提示
    toast.add({
      severity: 'info',
      summary: '開始轉換',
      detail: '正在準備轉換您的音檔，請稍候...',
      life: 3000
    })

    await transcribeAudio()
  } catch (error) {
    console.error('轉換失敗:', error)
    toast.add({
      severity: 'error',
      summary: '轉換失敗',
      detail: error instanceof Error ? error.message : '未知錯誤',
      life: 5000
    })
    projectStore.setTranscriptStatus('error', 0)
  }
}

const downloadTranscript = () => {
  downloadTranscriptFile()
  showDownloadMenu.value = false
}

const downloadNotes = () => {
  const content = socialWorkerNotes.value
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `社工補充說明_${new Date().toLocaleDateString('zh-TW')}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  showDownloadMenu.value = false
}

const downloadCombinedContent = () => {
  let content = ''

  if (transcript.value.trim()) {
    content += '=== 逐字稿內容 ===\n'
    content += transcript.value.trim() + '\n\n'
  }

  if (socialWorkerNotes.value.trim()) {
    content += '=== 社工補充說明 ===\n'
    content += socialWorkerNotes.value.trim()
  }

  if (!content.trim()) {
    toast.add({
      severity: 'warn',
      summary: '無內容可下載',
      detail: '請先輸入逐字稿或補充說明內容',
      life: 3000
    })
    return
  }

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `完整訪視內容_${new Date().toLocaleDateString('zh-TW')}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  showDownloadMenu.value = false

  toast.add({
    severity: 'success',
    summary: '下載完成',
    detail: '完整內容已下載',
    life: 3000
  })
}

const proceedToConfig = () => {
  sessionStore.setActiveTab(1) // 切換到記錄設定頁面
  projectStore.setCurrentStep('config')
}

// 語音輸入處理函數
const handleVoiceTranscript = (voiceText: string) => {
  // 將語音轉錄結果附加到現有的補充說明中
  if (socialWorkerNotes.value.trim()) {
    socialWorkerNotes.value += '\n\n' + voiceText.trim()
  } else {
    socialWorkerNotes.value = voiceText.trim()
  }

  toast.add({
    severity: 'success',
    summary: '語音輸入完成',
    detail: `已將語音轉錄結果添加到補充說明中`,
    life: 3000
  })
}

const handleVoiceProgress = (progress: number) => {
  // 可以顯示語音轉錄進度，這裡暫時不需要額外處理
}

const handleVoiceError = (error: string) => {
  toast.add({
    severity: 'error',
    summary: '語音輸入失敗',
    detail: error,
    life: 5000
  })
}

// 點擊外部關閉下載選單
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showDownloadMenu.value = false
  }
}

// 監聽點擊事件
document.addEventListener('click', handleClickOutside)
</script>

<style scoped>
.transcript-panel {
  max-width: 100%;
}

.player-card,
.transcript-card,
.notes-card {
  transition: all 0.3s ease;
}

.player-card:hover,
.transcript-card:hover,
.notes-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* 下載選單動畫 */
.download-menu {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 文字計數器樣式 */
.badge-counter {
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
