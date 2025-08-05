// stores/useProjectStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  AudioFile,
  ReportConfig,
  TreatmentConfig,
  ProjectData,
  StepType,
  StatusType
} from '@/types'

export const useProjectStore = defineStore('project', () => {
  // ==================== 基本狀態 ====================
  const projectId = ref<string | null>(null)
  const projectName = ref<string>('')
  const hasUploaded = ref<boolean>(false)
  const currentStep = ref<StepType>('transcript')

  // ==================== 錄音相關 ====================
  const audioFile = ref<File | null>(null)
  const audioUrl = ref<string>('')
  const recordingData = ref<Blob | null>(null)
  const isRecording = ref<boolean>(false)
  const isPaused = ref<boolean>(false)
  const recordingTime = ref<number>(0)

  // ==================== 逐字稿相關 ====================
  const transcript = ref<string>('')
  const socialWorkerNotes = ref<string>('')
  const transcriptStatus = ref<StatusType>('idle')
  const transcriptProgress = ref<number>(0)

  // ==================== 記錄設定相關 ====================
  const reportConfig = ref<ReportConfig>({
    // 必選項目 (預設包含)
    requiredSections: [
      // 一、主述議題
      'main_issue',

      // 二、個案概況
      'family_status',
      'children_status',
      'relationship_map',

      // 三、個案狀況 - 人身安全
      'safety_assessment',

      // 四、需求與評估
      'case_needs_and_expectations',
      'family_function_assessment',
      'overall_evaluation_and_recommendation'
    ],

    // 可選項目
    selectedSections: [],

    // 可選項目定義
    optionalSections: {
      '個案狀況 - 其他評估項目': [
        {
          value: 'legal_related_status',
          name: '個案狀況 - (一)法律相關狀況',
          icon: 'pi',
          description:
            '是否有訴訟(如民事離婚、保護令、暫時處份、強制執行、刑事案件-家暴、妨害性自主、法律爭議、法院未成年子女相關訴訟(如酌定親權-監護權、會面交往、給付扶養)、是否有犯罪服刑、涉及家庭暴力...等等)'
        },
        {
          value: 'economic_financial_status',
          name: '個案狀況 - (二)經濟或財務狀況',
          icon: 'pi',
          description:
            '主要收入來源、主要經濟提供者、是否有人身保險、是否負債、個案謀生能力、主要花費負擔'
        },
        {
          value: 'psychological_emotional_status',
          name: '個案狀況 - (三)心理或情緒狀況',
          icon: 'pi',
          description:
            '個案或其家人的人格特質、情緒穩定度、訪視的態度、身心狀況、是否有諮商或看精神科（或疾病史）、是否有自我傷害傾向、重大壓力事件'
        },
        {
          value: 'parenting_education_status',
          name: '個案狀況 - (四)教養或教育狀況',
          icon: 'pi',
          description:
            '個案或其家庭的親職能力、親職教養上的困難、孩子接受課後照顧或補習情形、孩子學業成績表現、學校中的師生關係、孩子與同儕的關係或互動、學業壓力'
        },
        {
          value: 'early_intervention_childcare_status',
          name: '個案狀況 - (五)早療或幼兒狀況',
          icon: 'pi',
          description:
            '個案與配偶之間的互動頻率、彼此情感支持狀況、家務責任分工、與孩子互動的頻率與深度、是否有隔代教養的問題、孩子與祖父母的情感關係、教養因應問題的策略或技巧'
        },
        {
          value: 'medical_physical_status',
          name: '個案狀況 - (六)醫療或生理狀況',
          icon: 'pi',
          description:
            '個案或其家人的罹病與診治史、對疾病的認識與態度、是否有長期用藥、是否具有身心障礙資格或有重大傷病卡、是否有慢性疾病或有重大疾病，服藥穩定度、對醫療的期待、醫療團隊的評估'
        },
        {
          value: 'support_system_status',
          name: '個案狀況 - (七)支持系統或狀況',
          icon: 'pi',
          description:
            '支持系統(正式系統、非正式系統)、主要照顧者、是否有委任律師、資源使用的能力、經常請教討論的對象、這些支持系統或支持者所提供的訊息或協助'
        },
        {
          value: 'cultural_traditional_status',
          name: '個案狀況 - (八)文化與傳統狀況',
          icon: 'pi',
          description:
            '國籍(若非台灣國籍)、民族(若非漢族)、宗教信仰背景、與台灣主流文化不同的生活習慣、生活價值觀、生活適應問題、語言溝通問題、與遠地或國外家人的關係'
        }
      ]
    }
  })

  // ==================== 記錄初稿相關 ====================
  const reportDraft = ref<string>('')
  const reportStatus = ref<StatusType>('idle')
  const reportProgress = ref<number>(0)

  // ==================== 處遇計畫相關 ====================
  const treatmentConfig = ref<TreatmentConfig>({
    selectedServiceDomains: []
  })

  const treatmentPlan = ref<string>('')
  const treatmentStatus = ref<StatusType>('idle')
  const treatmentProgress = ref<number>(0)

  // ==================== Computed ====================
  const canProceedToConfig = computed(() => {
    return transcript.value.trim().length > 0
  })

  const canGenerateReport = computed(() => {
    return (
      reportConfig.value.selectedSections.length > 0 ||
      reportConfig.value.requiredSections.length > 0
    )
  })

  const canProceedToTreatment = computed(() => {
    return reportDraft.value.trim().length > 0
  })

  const canGenerateTreatment = computed(() => {
    return treatmentConfig.value.selectedServiceDomains.length > 0
  })

  const totalSelectedSections = computed(() => {
    return reportConfig.value.requiredSections.length + reportConfig.value.selectedSections.length
  })

  const configValidation = computed(() => {
    if (totalSelectedSections.value === 0) {
      return { isValid: false, message: '請至少選擇一個記錄段落' }
    }
    return { isValid: true, message: '設定完成，可以生成記錄' }
  })

  const treatmentValidation = computed(() => {
    if (treatmentConfig.value.selectedServiceDomains.length === 0) {
      return { isValid: false, message: '請至少選擇一個社工服務領域' }
    }
    return { isValid: true, message: '設定完成，可以生成處遇計畫' }
  })

  // ==================== Actions ====================

  // 設置音檔
  const setAudioFile = (file: File, url: string) => {
    audioFile.value = file
    audioUrl.value = url
    hasUploaded.value = true
  }

  // 設置逐字稿
  const setTranscript = (text: string) => {
    transcript.value = text
    hasUploaded.value = true
  }

  // 更新逐字稿 (用於 streaming)
  const updateTranscript = (chunk: string) => {
    transcript.value += chunk
  }

  // 設置轉換狀態
  const setTranscriptStatus = (status: StatusType, progress: number = 0) => {
    transcriptStatus.value = status
    transcriptProgress.value = progress
  }

  // 更新記錄設定
  const updateReportConfig = (config: Partial<ReportConfig>) => {
    reportConfig.value = { ...reportConfig.value, ...config }
  }

  // 切換可選段落
  const toggleOptionalSection = (sectionValue: string) => {
    const index = reportConfig.value.selectedSections.indexOf(sectionValue)
    if (index > -1) {
      reportConfig.value.selectedSections.splice(index, 1)
    } else {
      reportConfig.value.selectedSections.push(sectionValue)
    }
  }

  // 全選某分類的段落
  const toggleCategorySection = (category: string, select: boolean) => {
    const sections = reportConfig.value.optionalSections[category] || []
    sections.forEach((section) => {
      const index = reportConfig.value.selectedSections.indexOf(section.value)
      if (select && index === -1) {
        reportConfig.value.selectedSections.push(section.value)
      } else if (!select && index > -1) {
        reportConfig.value.selectedSections.splice(index, 1)
      }
    })
  }

  // 更新記錄初稿 (用於 streaming)
  const updateReportDraft = (chunk: string) => {
    reportDraft.value += chunk
  }

  // 設置記錄狀態
  const setReportStatus = (status: StatusType, progress: number = 0) => {
    reportStatus.value = status
    reportProgress.value = progress
  }

  // 清空記錄初稿
  const clearReportDraft = () => {
    reportDraft.value = ''
    reportStatus.value = 'idle'
    reportProgress.value = 0
  }

  // 更新處遇計畫設定
  const updateTreatmentConfig = (config: Partial<TreatmentConfig>) => {
    treatmentConfig.value = { ...treatmentConfig.value, ...config }
  }

  // 切換處遇選項 - 簡化為只處理 selectedServiceDomains
  const toggleTreatmentOption = (type: 'selectedServiceDomains', value: string) => {
    const array = treatmentConfig.value[type]
    const index = array.indexOf(value)
    if (index > -1) {
      array.splice(index, 1)
    } else {
      array.push(value)
    }
  }

  // 更新處遇計畫 (用於 streaming)
  const updateTreatmentPlan = (chunk: string) => {
    treatmentPlan.value += chunk
  }

  // 設置處遇狀態
  const setTreatmentStatus = (status: StatusType, progress: number = 0) => {
    treatmentStatus.value = status
    treatmentProgress.value = progress
  }

  // 清空處遇計畫
  const clearTreatmentPlan = () => {
    treatmentPlan.value = ''
    treatmentStatus.value = 'idle'
    treatmentProgress.value = 0
  }

  // 切換步驟
  const setCurrentStep = (step: StepType) => {
    currentStep.value = step
  }

  // 儲存專案到 localStorage
  const saveProject = (): void => {
    const projectData: ProjectData = {
      projectId: projectId.value || Date.now().toString(),
      projectName: projectName.value || `專案_${new Date().toLocaleDateString()}`,
      audioFile: audioFile.value
        ? {
            file: audioFile.value,
            url: audioUrl.value,
            name: audioFile.value.name,
            size: audioFile.value.size,
            type: audioFile.value.type
          }
        : null,
      transcript: transcript.value,
      socialWorkerNotes: socialWorkerNotes.value,
      reportConfig: reportConfig.value,
      reportDraft: reportDraft.value,
      treatmentConfig: treatmentConfig.value,
      treatmentPlan: treatmentPlan.value,
      currentStep: currentStep.value,
      createdAt: projectId.value ? '' : new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    // 避免儲存 File 物件到 localStorage (會有問題)
    const saveData = {
      ...projectData,
      audioFile: projectData.audioFile
        ? {
            url: projectData.audioFile.url,
            name: projectData.audioFile.name,
            size: projectData.audioFile.size,
            type: projectData.audioFile.type
          }
        : null
    }

    localStorage.setItem(`social_work_project_${projectData.projectId}`, JSON.stringify(saveData))
    localStorage.setItem('social_work_current_project', projectData.projectId)

    projectId.value = projectData.projectId
    projectName.value = projectData.projectName
  }

  // 從 localStorage 載入專案
  const loadProject = (id: string): void => {
    const projectDataStr = localStorage.getItem(`social_work_project_${id}`)
    if (projectDataStr) {
      const projectData = JSON.parse(projectDataStr) as ProjectData

      projectId.value = projectData.projectId
      projectName.value = projectData.projectName
      audioUrl.value = projectData.audioFile?.url || ''
      transcript.value = projectData.transcript || ''
      socialWorkerNotes.value = projectData.socialWorkerNotes || ''
      reportConfig.value = projectData.reportConfig || reportConfig.value
      reportDraft.value = projectData.reportDraft || ''
      treatmentConfig.value = projectData.treatmentConfig || treatmentConfig.value
      treatmentPlan.value = projectData.treatmentPlan || ''
      currentStep.value = projectData.currentStep || 'transcript'
      hasUploaded.value = true
    }
  }

  // 重置專案
  const resetProject = (): void => {
    // 清除當前專案 ID
    if (projectId.value) {
      localStorage.removeItem(`social_work_project_${projectId.value}`)
      localStorage.removeItem('social_work_current_project')
    }

    // 重置所有狀態
    projectId.value = null
    projectName.value = ''
    hasUploaded.value = false
    currentStep.value = 'transcript'
    audioFile.value = null
    audioUrl.value = ''
    recordingData.value = null
    isRecording.value = false
    isPaused.value = false
    recordingTime.value = 0
    transcript.value = ''
    socialWorkerNotes.value = ''
    transcriptStatus.value = 'idle'
    transcriptProgress.value = 0
    reportConfig.value.selectedSections = []
    reportDraft.value = ''
    reportStatus.value = 'idle'
    reportProgress.value = 0
    treatmentConfig.value.selectedServiceDomains = []
    treatmentPlan.value = ''
    treatmentStatus.value = 'idle'
    treatmentProgress.value = 0
  }

  // 自動儲存當前專案
  const autoSave = (): void => {
    if (hasUploaded.value) {
      saveProject()
    }
  }

  return {
    // State
    projectId,
    projectName,
    hasUploaded,
    currentStep,
    audioFile,
    audioUrl,
    recordingData,
    isRecording,
    isPaused,
    recordingTime,
    transcript,
    socialWorkerNotes,
    transcriptStatus,
    transcriptProgress,
    reportConfig,
    reportDraft,
    reportStatus,
    reportProgress,
    treatmentConfig,
    treatmentPlan,
    treatmentStatus,
    treatmentProgress,

    // Computed
    canProceedToConfig,
    canGenerateReport,
    canProceedToTreatment,
    canGenerateTreatment,
    totalSelectedSections,
    configValidation,
    treatmentValidation,

    // Actions
    setAudioFile,
    setTranscript,
    updateTranscript,
    setTranscriptStatus,
    updateReportConfig,
    toggleOptionalSection,
    toggleCategorySection,
    updateReportDraft,
    setReportStatus,
    clearReportDraft,
    updateTreatmentConfig,
    toggleTreatmentOption,
    updateTreatmentPlan,
    setTreatmentStatus,
    clearTreatmentPlan,
    setCurrentStep,
    saveProject,
    loadProject,
    resetProject,
    autoSave
  }
})
