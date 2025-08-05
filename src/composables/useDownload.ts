// composables/useDownload.ts
import { useProjectStore } from '@/stores/useProjectStore'
import { fileUtils } from '@/utils/fileUtils'

export function useDownload() {
  const projectStore = useProjectStore()
  
  // 下載逐字稿和社工補充說明
  const downloadTranscript = (): void => {
    const content = [
      '=== 逐字稿內容 ===',
      projectStore.transcript,
      '',
      '=== 社工補充說明 ===',
      projectStore.socialWorkerNotes || '無補充說明'
    ].join('\n')
    
    const filename = fileUtils.generateFileName('transcript')
    fileUtils.downloadTextFile(content, filename)
  }
  
  // 下載記錄初稿
  const downloadReportDraft = (): void => {
    const content = [
      '=== 社工訪視記錄初稿 ===',
      '',
      projectStore.reportDraft,
      '',
      '=== 生成時間 ===',
      new Date().toLocaleString('zh-TW')
    ].join('\n')
    
    const filename = fileUtils.generateFileName('report_draft')
    fileUtils.downloadTextFile(content, filename)
  }
  
  // 下載處遇計畫
  const downloadTreatmentPlan = (): void => {
    const content = [
      '=== 處遇計畫 ===',
      '',
      projectStore.treatmentPlan,
      '',
      '=== 生成時間 ===',
      new Date().toLocaleString('zh-TW')
    ].join('\n')
    
    const filename = fileUtils.generateFileName('treatment_plan')
    fileUtils.downloadTextFile(content, filename)
  }
  
  // 下載完整專案報告
  const downloadFullReport = (): void => {
    const sections: string[] = []
    
    // 基本資訊
    sections.push('=== 專案資訊 ===')
    sections.push(`專案名稱: ${projectStore.projectName || '未命名專案'}`)
    sections.push(`建立時間: ${new Date().toLocaleString('zh-TW')}`)
    sections.push('')
    
    // 逐字稿
    if (projectStore.transcript) {
      sections.push('=== 逐字稿內容 ===')
      sections.push(projectStore.transcript)
      sections.push('')
    }
    
    // 社工補充說明
    if (projectStore.socialWorkerNotes) {
      sections.push('=== 社工補充說明 ===')
      sections.push(projectStore.socialWorkerNotes)
      sections.push('')
    }
    
    // 記錄初稿
    if (projectStore.reportDraft) {
      sections.push('=== 訪視記錄初稿 ===')
      sections.push(projectStore.reportDraft)
      sections.push('')
    }
    
    // 處遇計畫
    if (projectStore.treatmentPlan) {
      sections.push('=== 處遇計畫 ===')
      sections.push(projectStore.treatmentPlan)
      sections.push('')
    }
    
    const content = sections.join('\n')
    const filename = fileUtils.generateFileName('full_report')
    fileUtils.downloadTextFile(content, filename)
  }
  
  return {
    downloadTranscript,
    downloadReportDraft,
    downloadTreatmentPlan,
    downloadFullReport
  }
}