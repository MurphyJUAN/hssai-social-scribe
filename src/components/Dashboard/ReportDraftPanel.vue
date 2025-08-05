<!-- File: components/Dashboard/ReportDraftPanel.vue -->
<template>
  <div class="report-draft-panel space-y-6">
    <!-- 生成狀態顯示 -->
    <Card v-if="reportStatus === 'generating'" class="status-card">
      <template #content>
        <div class="text-center py-4">
          <div class="flex items-center justify-center gap-2 mb-4">
            <i class="pi pi-spin pi-spinner text-blue-600 text-xl"></i>
            <span class="text-lg font-medium text-blue-600">AI 正在生成記錄初稿...</span>
          </div>
          <ProgressBar :value="reportProgress" class="mb-2" />
          <p class="text-sm text-gray-600">請稍候，這可能需要幾分鐘時間</p>
        </div>
      </template>
    </Card>

    <!-- 記錄初稿內容 -->
    <Card v-if="reportDraft || reportStatus === 'generating'" class="draft-card">
      <template #title>
        <div class="flex items-center gap-2">
          <i class="pi pi-file-edit text-purple-600"></i>
          AI 生成記錄初稿
        </div>
      </template>
      <template #content>
        <Textarea
          v-model="reportDraft"
          placeholder="AI 生成的記錄初稿將在此顯示..."
          :rows="20"
          class="w-full resize-none"
          :disabled="reportStatus === 'generating'"
        />
      </template>
    </Card>

    <!-- 空狀態提示 -->
    <Card v-if="reportStatus === 'idle'" class="empty-state-card">
      <template #content>
        <div class="text-center py-12">
          <i class="pi pi-file-plus text-gray-400 text-4xl mb-4"></i>
          <h3 class="text-lg font-medium text-gray-600 mb-2">尚未生成記錄初稿</h3>
          <p class="text-gray-500 mb-4">請先完成記錄設定，然後點擊生成按鈕</p>
          <Button label="前往記錄設定" icon="pi pi-arrow-left" @click="goToConfig" outlined />
        </div>
      </template>
    </Card>

    <!-- 操作按鈕 -->
    <div v-if="reportDraft" class="flex justify-between items-center pt-4 border-t">
      <div class="text-sm text-gray-500">
        <span v-if="canProceedToTreatment" class="text-green-600 flex items-center gap-1">
          <i class="pi pi-check-circle"></i>
          記錄初稿已完成，可以進入處遇計畫設定
        </span>
      </div>

      <div class="flex gap-3">
        <Button
          label="下載記錄初稿"
          icon="pi pi-download"
          @click="downloadDraft"
          severity="secondary"
          outlined
        />
        <Button
          label="重新生成"
          icon="pi pi-refresh"
          @click="regenerateDraft"
          severity="secondary"
          outlined
        />
        <Button
          label="下一步：處遇計畫"
          icon="pi pi-arrow-right"
          @click="proceedToTreatment"
          :disabled="!canProceedToTreatment"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const projectStore = useProjectStore()
const sessionStore = useSessionStore()
const { generateReport } = useApiIntegration()
const { downloadReportDraft } = useDownload()

const { reportDraft, reportStatus, reportProgress, canProceedToTreatment } =
  storeToRefs(projectStore)

// Methods
const goToConfig = () => {
  sessionStore.setActiveTab(1) // 切換到記錄設定頁面
}

const downloadDraft = () => {
  downloadReportDraft()
}

const regenerateDraft = async () => {
  try {
    await generateReport()
  } catch (error) {
    console.error('重新生成失敗:', error)
  }
}

const proceedToTreatment = () => {
  sessionStore.setActiveTab(3) // 切換到處遇計畫頁面
  projectStore.setCurrentStep('treatment')
}
</script>
