<!-- File: components/Dashboard/TranscriptPanel.vue -->
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
            placeholder="逐字稿內容將在此顯示..."
            :rows="15"
            class="w-full resize-none"
            :disabled="transcriptStatus === 'processing'"
          />

          <!-- 轉換按鈕 (如果有音檔但沒有逐字稿) -->
          <div v-if="audioUrl" class="text-center">
            <Button
              label="開始轉換逐字稿"
              icon="pi pi-play"
              @click="startTranscription"
              :loading="transcriptStatus === 'processing'"
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
          其他補充說明（可用語音輸入）
        </div>
      </template>
      <template #content>
        <Textarea
          v-model="socialWorkerNotes"
          placeholder="請在此補充相關說明、觀察重點或其他需要記錄的資訊..."
          :rows="8"
          class="w-full resize-none"
        />
      </template>
    </Card>

    <!-- 操作按鈕區域 -->
    <div class="flex justify-between items-center pt-4 border-t">
      <div class="text-sm text-gray-500">
        <span v-if="canProceedToConfig" class="text-green-600 flex items-center gap-1">
          <i class="pi pi-check-circle"></i>
          逐字稿已完成，可以進入下一步
        </span>
        <span v-else class="text-orange-600 flex items-center gap-1">
          <i class="pi pi-exclamation-triangle"></i>
          請等待逐字稿轉換完成或上傳逐字稿內容
        </span>
      </div>

      <div class="flex gap-3">
        <Button
          label="下載逐字稿"
          icon="pi pi-download"
          @click="downloadTranscript"
          severity="secondary"
          outlined
          :disabled="!transcript.trim()"
        />
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
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useSessionStore } from '@/stores/useSessionStore'
import { useApiIntegration } from '@/composables/useApiIntegration'
import { useDownload } from '@/composables/useDownload'

// Components
import Card from 'primevue/card'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import AudioPlayer from '@/components/Common/AudioPlayer.vue'

const projectStore = useProjectStore()
const sessionStore = useSessionStore()
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

// Computed
const audioFileName = computed(() => {
  return audioFile.value?.name || '未知檔案'
})

// Methods
const startTranscription = async () => {
  try {
    await transcribeAudio()
  } catch (error) {
    console.error('轉換失敗:', error)
    // 可以加入錯誤提示
  }
}

const downloadTranscript = () => {
  downloadTranscriptFile()
}

const proceedToConfig = () => {
  sessionStore.setActiveTab(1) // 切換到記錄設定頁面
  projectStore.setCurrentStep('config')
}
</script>
