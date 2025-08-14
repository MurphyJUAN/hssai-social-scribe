<!-- File: views/HomeVuew.vue -->

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 主要內容區域 -->
    <main class="relative">
      <!-- Banner Upload 區域 -->
      <BannerUpload
        @audio-uploaded="handleAudioUpload"
        @transcript-uploaded="handleTranscriptUpload"
        @recording-completed="handleRecordingCompleted"
      />

      <!-- Dashboard 區域 (當 hasUploaded 為 true 時顯示) -->
      <div
        v-if="hasUploaded"
        class="container mx-auto px-2 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8"
        :class="{ 'pt-0 sm:pt-0': hasUploaded }"
      >
        <!-- 專案控制列 -->
        <div class="bg-white rounded-lg shadow-sm p-3 sm:p-4 mb-4 sm:mb-6">
          <!-- 手機版：垂直排列，桌面版：水平排列 -->
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 sm:gap-4">
            <!-- 專案資訊區域 -->
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 min-w-0">
              <h2 class="text-lg sm:text-xl font-semibold text-gray-800 truncate">
                {{ projectName || '新專案' }}
              </h2>
              <Badge
                :value="currentStepLabel"
                severity="info"
                class="text-xs sm:text-sm self-start sm:self-center"
              />
            </div>

            <!-- 按鈕區域 -->
            <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
              <Button
                label="儲存專案"
                icon="pi pi-save"
                @click="handleSaveProject"
                outlined
                size="small"
                class="w-full sm:w-auto text-sm justify-center"
              />
              <Button
                label="取消專案"
                icon="pi pi-times"
                @click="handleCancelProject"
                severity="secondary"
                outlined
                size="small"
                class="w-full sm:w-auto text-sm justify-center"
              />
            </div>
          </div>
        </div>

        <!-- Dashboard Panel -->
        <DashboardPanel>
          <!-- 逐字稿 Tab -->
          <template #transcript-tab>
            <TranscriptPanel />
          </template>

          <!-- 記錄設定 Tab -->
          <template #report-config-tab>
            <ReportConfigPanel />
          </template>

          <!-- 記錄初稿 Tab -->
          <template #ai-doc-tab>
            <ReportDraftPanel />
          </template>

          <!-- 處遇計畫設定 Tab -->
          <template #treatment-plan-tab>
            <TreatmentPlanPanel />
          </template>
        </DashboardPanel>
      </div>
    </main>

    <!-- 確認對話框 -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useSessionStore } from '@/stores/useSessionStore'
import { useConfirm } from 'primevue/useconfirm'
import type { StepType } from '@/types'

// Components
import BannerUpload from '@/components/Banner/BannerUpload.vue'
import DashboardPanel from '@/components/Dashboard/DashboardPanel.vue'
import TranscriptPanel from '@/components/Dashboard/TranscriptPanel.vue'
import ReportConfigPanel from '@/components/Dashboard/ReportConfigPanel.vue'
import ReportDraftPanel from '@/components/Dashboard/ReportDraftPanel.vue'
import TreatmentPlanPanel from '@/components/Dashboard/TreatmentPlanPanel.vue'

// PrimeVue
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import ConfirmDialog from 'primevue/confirmdialog'

// Interfaces
interface AudioUploadData {
  file: File
  url: string
}

interface TranscriptUploadData {
  transcript: string
  socialWorkerNotes: string
}

interface RecordingData {
  file: File
  url: string
}

const projectStore = useProjectStore()
const sessionStore = useSessionStore()
const { hasUploaded, currentStep, projectName } = storeToRefs(projectStore)

const confirm = useConfirm()

// Computed
const currentStepLabel = computed(() => {
  const stepLabels: Record<StepType, string> = {
    transcript: '逐字稿階段',
    config: '記錄設定階段',
    draft: '記錄初稿階段',
    treatment: '處遇計畫階段'
  }
  return stepLabels[currentStep.value] || '準備階段'
})

// Methods
const handleAudioUpload = (audioData: AudioUploadData) => {
  projectStore.setAudioFile(audioData.file, audioData.url)
  projectStore.setCurrentStep('transcript')
}

const handleTranscriptUpload = (transcriptData: TranscriptUploadData) => {
  projectStore.setTranscript(transcriptData.transcript)
  projectStore.setSocialWorkerNotes(transcriptData.socialWorkerNotes)
  projectStore.setCurrentStep('transcript')
}

const handleRecordingCompleted = (recordingData: RecordingData) => {
  projectStore.setAudioFile(recordingData.file, recordingData.url)
  projectStore.setCurrentStep('transcript')
}

const handleSaveProject = () => {
  try {
    projectStore.saveProject()
    // 可以加入成功提示
    console.log('專案已儲存')
  } catch (error) {
    console.error('儲存專案失敗:', error)
  }
}

const handleCancelProject = () => {
  confirm.require({
    message: '確定要取消當前專案嗎？所有未儲存的資料將會遺失。',
    header: '確認取消專案',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: '確認取消',
    rejectLabel: '繼續編輯',
    accept: () => {
      projectStore.resetProject()
      sessionStore.resetTab()
    }
  })
}

// Lifecycle
onMounted(() => {
  // 檢查是否有進行中的專案
  const currentProjectId = localStorage.getItem('social_work_current_project')
  if (currentProjectId) {
    projectStore.loadProject(currentProjectId)
  }
})
</script>

<style scoped>
/* 確保在小螢幕上按鈕文字不會太小 */
@media (max-width: 640px) {
  :deep(.p-button-label) {
    font-size: 0.875rem;
  }

  /* 確保 Badge 在手機上不會太大 */
  :deep(.p-badge) {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
}

/* 中等螢幕的微調 */
@media (min-width: 641px) and (max-width: 1024px) {
  :deep(.p-button-label) {
    font-size: 0.875rem;
  }
}
</style>
