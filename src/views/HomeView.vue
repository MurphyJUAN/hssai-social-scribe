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
      <div v-if="hasUploaded" class="container mx-auto px-4 py-8" :class="{ 'pt-0': hasUploaded }">
        <!-- 專案控制列 -->
        <div class="flex justify-between items-center mb-6 bg-white rounded-lg shadow-sm p-4">
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-semibold text-gray-800">
              {{ projectName || '新專案' }}
            </h2>
            <Badge :value="currentStepLabel" severity="info" class="text-sm" />
          </div>

          <div class="flex gap-3">
            <Button
              label="儲存專案"
              icon="pi pi-save"
              @click="handleSaveProject"
              outlined
              size="small"
            />
            <Button
              label="取消專案"
              icon="pi pi-times"
              @click="handleCancelProject"
              severity="secondary"
              outlined
              size="small"
            />
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
  content: string
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
  projectStore.setTranscript(transcriptData.content)
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
