<!-- File: components/Dashboard/ReportConfigPanel.vue -->
<template>
  <div class="report-config-panel p-6">
    <!-- 頁面標題 -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">記錄設定</h2>
      <p class="text-gray-600">選擇需要生成的記錄段落</p>
    </div>

    <!-- 段落選擇區域 -->
    <Card class="mb-6">
      <template #title>
        <span class="flex items-center gap-2">
          <i class="pi pi-list text-green-600"></i>
          段落選擇
        </span>
      </template>
      <template #content>
        <div class="space-y-6">
          <!-- 預設包含段落說明 -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-3">
              <i class="pi pi-info-circle text-blue-600"></i>
              <h4 class="font-medium text-blue-800">以下段落將預設包含在記錄中</h4>
            </div>
            <p class="text-sm text-blue-700 mb-4">
              基於基本資訊整理需求與潛在安全性問題評估，以下段落為社工訪視記錄必要內容，系統將自動包含。
            </p>

            <!-- 按段落分組顯示 -->
            <div class="space-y-4">
              <!-- 一、主述議題 -->
              <div class="bg-white border border-blue-100 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-2">
                  <i class="pi pi-exclamation-triangle text-blue-600"></i>
                  <h5 class="font-medium text-blue-800">一、主述議題</h5>
                </div>
                <p class="text-xs text-blue-700 mb-2">建立案件基本脈絡，確保服務導向正確</p>
                <div class="space-y-1">
                  <div
                    v-for="section in getRequiredSectionsByGroup('main')"
                    :key="section"
                    class="text-sm text-blue-800 pl-4"
                  >
                    • {{ getSectionDisplayName(section) }}
                  </div>
                </div>
              </div>

              <!-- 二、個案概況 -->
              <div class="bg-white border border-blue-100 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-2">
                  <i class="pi pi-users text-blue-600"></i>
                  <h5 class="font-medium text-blue-800">二、個案概況</h5>
                </div>
                <p class="text-xs text-blue-700 mb-2">完整了解家庭結構與背景，為後續評估奠定基礎</p>
                <div class="space-y-1">
                  <div
                    v-for="section in getRequiredSectionsByGroup('case_overview')"
                    :key="section"
                    class="text-sm text-blue-800 pl-4"
                  >
                    • {{ getSectionDisplayName(section) }}
                  </div>
                </div>
              </div>

              <!-- 三、個案狀況 - 人身安全 -->
              <div class="bg-white border border-blue-100 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-2">
                  <i class="pi pi-shield text-blue-600"></i>
                  <h5 class="font-medium text-blue-800">三、個案狀況 - 人身安全</h5>
                </div>
                <p class="text-xs text-blue-700 mb-2">風險評估必要項目，確保服務對象安全</p>
                <div class="space-y-1">
                  <div
                    v-for="section in getRequiredSectionsByGroup('safety')"
                    :key="section"
                    class="text-sm text-blue-800 pl-4"
                  >
                    • {{ getSectionDisplayName(section) }}
                  </div>
                </div>
              </div>

              <!-- 四、需求與評估 -->
              <div class="bg-white border border-blue-100 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-2">
                  <i class="pi pi-chart-line text-blue-600"></i>
                  <h5 class="font-medium text-blue-800">四、需求與評估</h5>
                </div>
                <p class="text-xs text-blue-700 mb-2">專業評估與服務規劃，確保介入有效性</p>
                <div class="space-y-1">
                  <div
                    v-for="section in getRequiredSectionsByGroup('assessment')"
                    :key="section"
                    class="text-sm text-blue-800 pl-4"
                  >
                    • {{ getSectionDisplayName(section) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 額外選擇段落 -->
          <div>
            <div class="flex items-center gap-2 mb-4">
              <i class="pi pi-plus-circle text-gray-600"></i>
              <h4 class="font-medium text-gray-800">三、個案狀況 - 其他評估項目</h4>
              <span class="text-sm text-gray-500">（可依個案需求選擇）</span>
            </div>
            <p class="text-sm text-gray-600 mb-4">
              社工可依據個案特性與服務需求，選擇適合的評估面向進行深入了解。
            </p>

            <!-- 全選/取消全選 (僅針對可選項目) -->
            <div class="flex items-center gap-2 mb-4 p-3 bg-gray-50 rounded-lg">
              <Checkbox
                v-model="selectAllOptional"
                :binary="true"
                @change="onSelectAllOptionalChange"
              />
              <label
                class="font-medium text-gray-700 cursor-pointer"
                @click="toggleSelectAllOptional"
              >
                全選其他評估項目 ({{ selectedOptionalCount }}/{{ totalOptionalCount }})
              </label>
            </div>

            <!-- 可選段落選項 (單一分類) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div
                v-for="section in getSectionsForCategory('個案狀況 - 其他評估項目')"
                :key="section.value"
                class="flex items-start gap-3 p-4 border rounded-lg transition-colors bg-white hover:bg-gray-50 cursor-pointer"
                @click="toggleSection(section.value)"
              >
                <Checkbox
                  v-model="reportConfig.selectedSections"
                  :value="section.value"
                  @change="onSectionChange"
                  @click.stop
                  class="mt-1"
                  :binary="false"
                />
                <div class="flex-1 min-w-0">
                  <label
                    class="text-sm font-medium cursor-pointer block flex items-center gap-2 text-gray-800 mb-2"
                  >
                    <i :class="[section.icon, 'text-gray-600']"></i>
                    {{ section.name }}
                  </label>
                  <p class="text-xs text-gray-600 leading-relaxed">
                    {{ section.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- 選擇摘要 -->
    <Card class="mb-6" v-if="totalSelectedSections > 0">
      <template #title>
        <span class="flex items-center gap-2">
          <i class="pi pi-check-circle text-green-600"></i>
          選擇摘要
        </span>
      </template>
      <template #content>
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-medium text-green-800">已選擇的記錄段落</h4>
            <Badge :value="`共 ${totalSelectedSections} 項`" severity="success" />
          </div>

          <div class="space-y-2">
            <!-- 必選項目 -->
            <div>
              <h5 class="text-sm font-medium text-green-700 mb-2">
                必選項目 ({{ reportConfig.requiredSections.length }} 項)
              </h5>
              <div class="flex flex-wrap gap-2"></div>
            </div>

            <!-- 可選項目 -->
            <div v-if="reportConfig.selectedSections.length > 0">
              <h5 class="text-sm font-medium text-green-700 mb-2">
                可選項目 ({{ reportConfig.selectedSections.length }} 項)
              </h5>
              <div class="flex flex-wrap gap-2">
                <Tag
                  v-for="section in reportConfig.selectedSections"
                  :key="section"
                  :value="getSectionDisplayName(section)"
                  severity="success"
                  class="text-xs"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- 操作按鈕 -->
    <div
      class="flex flex-col sm:flex-row sm:justify-between sm:items-center pt-4 border-t gap-3 sm:gap-0"
    >
      <div class="text-sm text-gray-500 order-2 sm:order-1">
        <span v-if="configValidation.isValid" class="text-green-600 flex items-center gap-1">
          <i class="pi pi-check-circle text-xs sm:text-sm"></i>
          <span class="text-xs sm:text-sm">{{ configValidation.message }}</span>
        </span>
        <span v-else class="text-orange-600 flex items-center gap-1">
          <i class="pi pi-exclamation-triangle text-xs sm:text-sm"></i>
          <span class="text-xs sm:text-sm">{{ configValidation.message }}</span>
        </span>
      </div>

      <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 order-1 sm:order-2">
        <Button
          label="重置"
          icon="pi pi-refresh"
          severity="secondary"
          @click="resetConfig"
          outlined
          size="small"
          class="w-full sm:w-auto text-sm justify-center sm:hidden"
        />

        <Button
          label="重置設定"
          icon="pi pi-refresh"
          severity="secondary"
          @click="resetConfig"
          outlined
          size="small"
          class="hidden sm:flex w-auto text-sm justify-center"
        />

        <Button
          label="下一步"
          icon="pi pi-arrow-right"
          :disabled="!configValidation.isValid && reportStatus !== 'generating'"
          @click="proceedToReport"
          size="small"
          class="w-full sm:w-auto text-sm justify-center font-medium sm:hidden"
        />

        <Button
          label="下一步：生成記錄"
          icon="pi pi-arrow-right"
          :disabled="!configValidation.isValid && reportStatus !== 'generating'"
          @click="proceedToReport"
          size="small"
          class="hidden sm:flex w-auto text-sm justify-center font-medium"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useSessionStore } from '@/stores/useSessionStore'
import { useApiIntegration } from '@/composables/useApiIntegration'
import type { ReportSection } from '@/types'

// PrimeVue Components
import Card from 'primevue/card'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import Tag from 'primevue/tag'

// Stores and composables
const projectStore = useProjectStore()
const sessionStore = useSessionStore()
const { generateReport } = useApiIntegration()

const { reportConfig, reportStatus, configValidation, totalSelectedSections } =
  storeToRefs(projectStore)

// Local reactive state
const selectAllOptional = ref(false)

// 段落顯示名稱對照
const sectionDisplayNames: Record<string, string> = {
  // 必選項目
  main_issue: '主述議題',
  family_status: '家庭狀況',
  children_status: '子女狀況',
  relationship_map: '人物關係圖(未完成)',
  safety_assessment: '人身或安全狀況',
  case_needs_and_expectations: '個案需求與期待',
  family_function_assessment: '家庭功能評估',
  overall_evaluation_and_recommendation: '整體評估建議',

  // 可選項目
  legal_related_status: '個案狀況 - (一)法律相關狀況',
  economic_financial_status: '個案狀況 - (二)經濟或財務狀況',
  psychological_emotional_status: '個案狀況 - (三)心理或情緒狀況',
  parenting_education_status: '個案狀況 - (四)教養或教育狀況',
  early_intervention_childcare_status: '個案狀況 - (五)早療或幼兒狀況',
  medical_physical_status: '個案狀況 - (六)醫療或生理狀況',
  support_system_status: '個案狀況 - (七)支持系統或狀況',
  cultural_traditional_status: '個案狀況 - (八)文化與傳統狀況'
}

// 必選項目分組
const requiredSectionGroups: Record<string, string[]> = {
  main: ['main_issue'],
  case_overview: ['family_status', 'children_status', 'relationship_map'],
  safety: ['safety_assessment'],
  assessment: [
    'case_needs_and_expectations',
    'family_function_assessment',
    'overall_evaluation_and_recommendation'
  ]
}

// Computed properties
const optionalCategories = computed(() => {
  return Object.keys(reportConfig.value.optionalSections)
})

const totalOptionalCount = computed(() => {
  return Object.values(reportConfig.value.optionalSections).flat().length
})

const selectedOptionalCount = computed(() => {
  return reportConfig.value.selectedSections.length
})

// 檢查是否全選了可選項目
const isAllOptionalSelected = computed(() => {
  return selectedOptionalCount.value === totalOptionalCount.value
})

// 監聽全選狀態變化
const updateSelectAllOptional = () => {
  selectAllOptional.value = isAllOptionalSelected.value
}

// Methods
const getSectionDisplayName = (sectionKey: string): string => {
  return sectionDisplayNames[sectionKey] || sectionKey
}

const getRequiredSectionsByGroup = (group: string): string[] => {
  return requiredSectionGroups[group] || []
}

const getSectionsForCategory = (category: string): ReportSection[] => {
  return reportConfig.value.optionalSections[category] || []
}

const toggleSection = (sectionValue: string): void => {
  projectStore.toggleOptionalSection(sectionValue)
  updateSelectAllOptional()
}

const onSectionChange = (): void => {
  updateSelectAllOptional()
}

const toggleSelectAllOptional = (): void => {
  selectAllOptional.value = !selectAllOptional.value
  onSelectAllOptionalChange()
}

const onSelectAllOptionalChange = (): void => {
  if (selectAllOptional.value) {
    // 全選所有可選項目
    Object.values(reportConfig.value.optionalSections)
      .flat()
      .forEach((section) => {
        if (!reportConfig.value.selectedSections.includes(section.value)) {
          reportConfig.value.selectedSections.push(section.value)
        }
      })
  } else {
    // 取消全選
    reportConfig.value.selectedSections = []
  }
}

const resetConfig = (): void => {
  reportConfig.value.selectedSections = []
  selectAllOptional.value = false
}

const proceedToReport = async (): Promise<void> => {
  try {
    // 切換到記錄初稿頁面
    sessionStore.setActiveTab(2)
    projectStore.setCurrentStep('draft')

    await nextTick()
    await new Promise((resolve) => setTimeout(resolve, 200)) // 確保組件完全掛載

    projectStore.setReportStatus('generating', 0)

    await nextTick()

    // 開始生成記錄
    await generateReport()
  } catch (error) {
    console.error('生成記錄失敗:', error)
    projectStore.setReportStatus('error', 0)
    // 可以加入錯誤提示
  }
}

// 初始化全選狀態
updateSelectAllOptional()
</script>

<style scoped>
/* 段落項目 hover 效果 */
.section-item:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

/* Tag 樣式調整 */
:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

/* Badge 樣式調整 */
:deep(.p-badge) {
  font-size: 0.75rem;
}

/* 選擇摘要動畫 */
.summary-animation {
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

/* Checkbox 對齊調整 */
:deep(.p-checkbox) {
  margin-top: 0.125rem;
}
/* 確保按鈕在小螢幕上有適當的觸控區域 */
@media (max-width: 640px) {
  :deep(.p-button) {
    min-height: 44px;
    padding: 0.5rem 1rem;
  }

  :deep(.p-button-label) {
    font-size: 0.875rem;
  }

  :deep(.p-button-icon) {
    font-size: 0.875rem;
  }
}

/* 狀態訊息在小螢幕上的微調 */
@media (max-width: 640px) {
  .text-gray-500 span {
    justify-content: center;
  }
}
</style>
