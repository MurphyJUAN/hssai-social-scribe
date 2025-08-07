// composables/useApiIntegration.ts
import { ref } from 'vue'
import { useProjectStore } from '@/stores/useProjectStore'
import { apiService } from '@/services/apiService'

export function useApiIntegration() {
  const projectStore = useProjectStore()
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // 轉換音檔為逐字稿
  const transcribeAudio = async (): Promise<void> => {
    if (!projectStore.audioFile) {
      throw new Error('沒有音檔可以轉換')
    }

    try {
      isLoading.value = true
      error.value = null

      projectStore.setTranscriptStatus('processing', 0)

      const transcript = await apiService.transcribeAudio(
        projectStore.audioFile,
        (progress: number, partialTranscript?: string) => {
          projectStore.setTranscriptStatus('processing', progress)
          if (partialTranscript) {
            projectStore.transcript = partialTranscript
          }
        }
      )

      projectStore.setTranscript(transcript)
      projectStore.setTranscriptStatus('completed', 100)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '轉換失敗'
      error.value = errorMessage
      projectStore.setTranscriptStatus('error', 0)
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  // 生成記錄初稿
  const generateReport = async (): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      projectStore.setReportStatus('generating', 0)
      projectStore.clearReportDraft()

      const reportData = {
        transcript: projectStore.transcript,
        socialWorkerNotes: projectStore.socialWorkerNotes,
        selectedSections: projectStore.reportConfig.selectedSections,
        requiredSections: projectStore.reportConfig.requiredSections
      }

      console.log('>>>reportData', reportData)

      const report = await apiService.generateReport(
        reportData,
        (progress: number, partialReport?: string) => {
          projectStore.setReportStatus('generating', progress)
          if (partialReport) {
            projectStore.reportDraft = partialReport
          }
        }
      )

      projectStore.reportDraft = report
      projectStore.setReportStatus('completed', 100)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '生成失敗'
      error.value = errorMessage
      projectStore.setReportStatus('error', 0)
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  // 生成處遇計畫
  const generateTreatmentPlan = async (): Promise<void> => {
    try {
      isLoading.value = true
      error.value = null

      projectStore.setTreatmentStatus('generating', 0)
      projectStore.clearTreatmentPlan()

      const treatmentData = {
        reportDraft: projectStore.reportDraft,
        selectedServiceDomains: projectStore.treatmentConfig.selectedServiceDomains
      }

      const plan = await apiService.generateTreatmentPlan(
        treatmentData,
        (progress: number, partialPlan?: string) => {
          projectStore.setTreatmentStatus('generating', progress)
          if (partialPlan) {
            projectStore.treatmentPlan = partialPlan
          }
        }
      )

      projectStore.treatmentPlan = plan
      projectStore.setTreatmentStatus('completed', 100)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '生成失敗'
      error.value = errorMessage
      projectStore.setTreatmentStatus('error', 0)
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    transcribeAudio,
    generateReport,
    generateTreatmentPlan
  }
}
