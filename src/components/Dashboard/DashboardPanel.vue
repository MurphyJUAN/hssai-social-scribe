<!-- File: components/Dashboard/DashboardPanel.vue -->
<template>
  <div class="w-full">
    <!-- 專案標題區域 (slot) -->
    <slot name="project-header"></slot>

    <!-- Tab 導航 -->
    <TabView
      v-model:activeIndex="activeTabIndex"
      :pt="{
        tabpanel: {
          headerAction: ({ parent, context }) => ({
            class: [
              'relative font-bold flex items-center p-5 -mb-[2px] border-b-2 rounded-t-md',
              'transition-all duration-200',
              'focus-visible:outline-none focus-visible:ring focus-visible:ring-inset',
              'cursor-pointer select-none',

              // 根據 tab 狀態設定樣式
              context.index === parent.state.d_activeIndex
                ? 'text-deepBlue border-deepBlue bg-white'
                : 'text-lightPurple border-transparent hover:text-deepBlue hover:border-deepBlue bg-gray-50 hover:bg-white',

              // 禁用狀態
              isTabDisabled(context.index)
                ? 'opacity-50 cursor-not-allowed hover:text-lightPurple hover:border-transparent hover:bg-gray-50'
                : ''
            ]
          }),
          root: {
            class: 'bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden'
          }
        }
      }"
    >
      <!-- 逐字稿 Tab -->
      <TabPanel header="逐字稿" :disabled="isTabDisabled(0)">
        <template #header>
          <div class="flex items-center gap-2">
            <i class="pi pi-file-text"></i>
            <!-- <span>逐字稿</span> -->
            <Badge
              v-if="transcriptStatus === 'processing'"
              value="轉換中"
              severity="info"
              class="text-xs"
            />
            <Badge
              v-else-if="transcript.trim()"
              value="已完成"
              severity="success"
              class="text-xs"
            />
          </div>
        </template>
        <slot name="transcript-tab" />
      </TabPanel>

      <!-- 記錄設定 Tab -->
      <TabPanel header="記錄設定" :disabled="isTabDisabled(1)">
        <template #header>
          <div class="flex items-center gap-2">
            <i class="pi pi-cog"></i>
            <!-- <span>記錄設定</span> -->
            <Badge
              v-if="totalSelectedSections > 0"
              :value="`已選 ${totalSelectedSections} 項`"
              severity="info"
              class="text-xs"
            />
          </div>
        </template>
        <slot name="report-config-tab" />
      </TabPanel>

      <!-- 記錄初稿 Tab -->
      <TabPanel header="記錄初稿" :disabled="isTabDisabled(2)">
        <template #header>
          <div class="flex items-center gap-2">
            <i class="pi pi-file-edit"></i>
            <!-- <span>記錄初稿</span> -->
            <Badge
              v-if="reportStatus === 'generating'"
              value="生成中"
              severity="warning"
              class="text-xs"
            />
            <Badge
              v-else-if="reportDraft.trim()"
              value="已完成"
              severity="success"
              class="text-xs"
            />
            <Badge
              v-else-if="reportStatus === 'error'"
              value="生成失敗"
              severity="danger"
              class="text-xs"
            />
          </div>
        </template>
        <slot name="ai-doc-tab" />
      </TabPanel>

      <!-- 處遇計畫設定 Tab -->
      <TabPanel header="處遇計畫設定" :disabled="isTabDisabled(3)">
        <template #header>
          <div class="flex items-center gap-2">
            <i class="pi pi-target"></i>
            <!-- <span>處遇計畫設定</span> -->
            <Badge
              v-if="treatmentStatus === 'generating'"
              value="生成中"
              severity="warning"
              class="text-xs"
            />
            <Badge
              v-else-if="treatmentPlan.trim()"
              value="已完成"
              severity="success"
              class="text-xs"
            />
            <Badge
              v-else-if="treatmentValidation.isValid"
              value="可生成"
              severity="info"
              class="text-xs"
            />
          </div>
        </template>
        <slot name="treatment-plan-tab" />
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useSessionStore } from '@/stores/useSessionStore'
import type { StepType } from '@/types'

// PrimeVue Components
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Badge from 'primevue/badge'

// Stores
const projectStore = useProjectStore()
const sessionStore = useSessionStore()

// Reactive data from stores
const { activeTabIndex, canGoNext, canGoPrev } = storeToRefs(sessionStore)
const {
  transcript,
  transcriptStatus,
  totalSelectedSections,
  reportDraft,
  reportStatus,
  treatmentPlan,
  treatmentStatus,
  treatmentValidation,
  canProceedToConfig,
  canGenerateReport,
  canProceedToTreatment,
  canGenerateTreatment,
  currentStep
} = storeToRefs(projectStore)

// 步驟定義
const steps = [
  { key: 'transcript', label: '逐字稿', required: true },
  { key: 'config', label: '記錄設定', required: true },
  { key: 'draft', label: '記錄初稿', required: false },
  { key: 'treatment', label: '處遇計畫', required: false }
] as const

// Computed properties
const currentStepLabel = computed(() => {
  const stepLabels: Record<StepType, string> = {
    transcript: '逐字稿階段',
    config: '記錄設定階段',
    draft: '記錄初稿階段',
    treatment: '處遇計畫階段'
  }
  return stepLabels[currentStep.value] || '準備階段'
})

const currentStepHint = computed(() => {
  const hints: Record<number, { title: string; description: string } | null> = {
    0: transcript.value.trim()
      ? null
      : {
          title: '開始建立逐字稿',
          description:
            '上傳音檔讓 AI 自動轉換，或直接上傳已有的逐字稿檔案。完成後可以添加社工補充說明。'
        },
    1:
      totalSelectedSections.value > 0
        ? null
        : {
            title: '設定記錄內容',
            description:
              '選擇需要包含在訪視記錄中的段落。系統已預設必要項目，您可以根據個案需求選擇額外的評估面向。'
          },
    2: reportDraft.value.trim()
      ? null
      : {
          title: '生成記錄初稿',
          description: '基於逐字稿內容和選定的記錄段落，AI 將為您生成專業的訪視記錄初稿。'
        },
    3: treatmentPlan.value.trim()
      ? null
      : {
          title: '制定處遇計畫',
          description: '選擇處遇目標、方法和資源，設定時程後，AI 將協助您生成完整的處遇計畫。'
        }
  }
  return hints[activeTabIndex.value]
})

// Tab 禁用邏輯
const isTabDisabled = (tabIndex: number): boolean => {
  switch (tabIndex) {
    case 0: // 逐字稿 - 永遠可用
      return false
    case 1: // 記錄設定 - 永遠可用
      return false
    case 2: // 記錄初稿 - 需要有逐字稿
      return !transcript.value.trim()
    case 3: // 處遇計畫 - 永遠可用
      return false
    default:
      return false
  }
}

// 是否可以進入下一步
const canProceedToNext = computed(() => {
  switch (activeTabIndex.value) {
    case 0: // 逐字稿 → 記錄設定
      return canProceedToConfig.value
    case 1: // 記錄設定 → 記錄初稿
      return canGenerateReport.value
    case 2: // 記錄初稿 → 處遇計畫
      return canProceedToTreatment.value
    case 3: // 處遇計畫 → 無下一步
      return false
    default:
      return false
  }
})

// 取得下一步按鈕標籤
const getNextStepLabel = (): string => {
  switch (activeTabIndex.value) {
    case 0:
      return '下一步：記錄設定'
    case 1:
      return '下一步：記錄初稿'
    case 2:
      return '下一步：處遇計畫'
    default:
      return '下一步'
  }
}

// 取得步驟指示器樣式
const getStepIndicatorClass = (stepIndex: number): string => {
  if (stepIndex < activeTabIndex.value) {
    return 'bg-green-500' // 已完成
  } else if (stepIndex === activeTabIndex.value) {
    return 'bg-blue-500' // 目前步驟
  } else {
    return 'bg-gray-300' // 未完成
  }
}

// Methods
const prevStep = () => {
  if (canGoPrev.value) {
    sessionStore.prevTab()
    updateCurrentStep()
  }
}

const nextStep = () => {
  if (canGoNext.value && canProceedToNext.value) {
    sessionStore.nextTab()
    updateCurrentStep()
  }
}

const updateCurrentStep = () => {
  const stepKeys: StepType[] = ['transcript', 'config', 'draft', 'treatment']
  const newStep = stepKeys[activeTabIndex.value]
  if (newStep) {
    projectStore.setCurrentStep(newStep)
  }
}

const saveProject = () => {
  try {
    projectStore.saveProject()
    // 可以加入成功提示
    console.log('專案已儲存')
  } catch (error) {
    console.error('儲存專案失敗:', error)
    // 可以加入錯誤提示
  }
}
</script>

<style scoped>
/* 自定義 Tab 樣式 */
:deep(.p-tabview-nav) {
  background: transparent;
  border: none;
}

:deep(.p-tabview-panels) {
  background: transparent;
  border: none;
  padding: 1.5rem 0 0 0;
}

:deep(.p-tabview-panel) {
  background: transparent;
}

/* 步驟指示器動畫 */
.step-indicator {
  transition: all 0.3s ease;
}

/* 快速操作區域樣式 */
.quick-actions {
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 提示區域動畫 */
.hint-animation {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Badge 自定義樣式 */
:deep(.p-badge) {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
}

/* 禁用狀態的 Tab */
:deep(.p-tabview-nav li.p-disabled) {
  opacity: 0.5;
  pointer-events: none;
}

/* Tab hover 效果 */
:deep(.p-tabview-nav li:not(.p-disabled)) {
  transition: all 0.2s ease;
}

:deep(.p-tabview-nav li:not(.p-disabled):hover) {
  transform: translateY(-1px);
}
</style>
