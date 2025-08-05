// File: types/index.ts
export interface AudioFile {
  file: File
  url: string
  name: string
  size: number
  type: string
}

export interface ReportSection {
  value: string
  name: string
  icon: string
  description: string
}

export interface ReportConfig {
  requiredSections: string[]
  selectedSections: string[]
  optionalSections: Record<string, ReportSection[]>
}

export interface TreatmentOption {
  value: string
  name: string
  category: string
}

export interface TreatmentConfig {
  selectedServiceDomains: string[]
}

export interface ProjectData {
  projectId: string
  projectName: string
  audioFile: AudioFile | null
  transcript: string
  socialWorkerNotes: string
  reportConfig: ReportConfig
  reportDraft: string
  treatmentConfig: TreatmentConfig
  treatmentPlan: string
  currentStep: StepType
  createdAt: string
  updatedAt: string
}

export type StepType = 'transcript' | 'config' | 'draft' | 'treatment'
export type StatusType = 'idle' | 'processing' | 'generating' | 'completed' | 'error'
