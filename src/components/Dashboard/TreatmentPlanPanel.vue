<!-- File: components/Dashboard/TreatmentPlanPanel.vue -->
<template>
  <div class="treatment-plan-panel space-y-6">
    <!-- 社工服務領域設定 -->
    <Card class="config-card">
      <template #title>
        <div class="flex items-center gap-2">
          <i class="pi pi-target text-blue-600 text-sm sm:text-base"></i>
          <span class="text-base sm:text-2xl">處遇計畫設定</span>
          <p class="text-sm sm:text-lg text-gray-600">(可選擇個案所需要的處遇方向)</p>
        </div>
      </template>
      <template #content>
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="domain in serviceDomains"
              :key="domain.value"
              class="flex items-center gap-3 p-3 border rounded-lg bg-white hover:bg-gray-50 cursor-pointer"
              @click="toggleServiceDomain(domain.value)"
            >
              <Checkbox
                v-model="treatmentConfig.selectedServiceDomains"
                :value="domain.value"
                :binary="false"
                @click.stop
              />
              <label class="text-sm font-medium cursor-pointer">
                {{ domain.name }}
              </label>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- 處遇計畫內容 -->
    <Card v-if="treatmentPlan || treatmentStatus === 'generating'" class="plan-card">
      <template #title>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="pi pi-file-edit text-indigo-600"></i>
            AI 生成處遇計畫
          </div>
          <div
            v-if="treatmentStatus === 'generating'"
            class="flex items-center gap-2 text-sm text-blue-600"
          >
            <i class="pi pi-spin pi-spinner"></i>
            生成中... {{ treatmentProgress }}%
          </div>
        </div>
        <div
          class="mt-2 text-sm text-orange-600 bg-orange-50 p-2 rounded border-l-4 border-orange-400"
        >
          <i class="pi pi-exclamation-triangle mr-2"></i>
          (請注意，AI生成的結果可能會有錯誤或疏漏，請使用者仔細確認並自行增補。)
        </div>
      </template>
      <template #content>
        <div class="space-y-4">
          <ProgressBar
            v-if="treatmentStatus === 'generating'"
            :value="treatmentProgress"
            class="mb-4"
          />
          <Textarea
            v-model="treatmentPlan"
            placeholder="AI 生成的處遇計畫將在此顯示..."
            :rows="15"
            class="w-full resize-none"
            :disabled="treatmentStatus === 'generating'"
          />
        </div>
      </template>
    </Card>

    <!-- 操作按鈕 -->
    <div
      class="flex flex-col sm:flex-row sm:justify-between sm:items-center pt-4 border-t gap-3 sm:gap-0"
    >
      <div class="text-sm text-gray-500 order-2 sm:order-1">
        <span
          v-if="treatmentValidation.isValid"
          class="text-green-600 flex items-center gap-1 justify-center sm:justify-start"
        >
          <i class="pi pi-check-circle text-xs sm:text-sm"></i>
          <span class="text-xs sm:text-sm text-center sm:text-left">
            {{ treatmentValidation.message }}
          </span>
        </span>
        <span
          v-else
          class="text-orange-600 flex items-center gap-1 justify-center sm:justify-start"
        >
          <i class="pi pi-exclamation-triangle text-xs sm:text-sm"></i>
          <span class="text-xs sm:text-sm text-center sm:text-left">
            {{ treatmentValidation.message }}
          </span>
        </span>
      </div>

      <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 order-1 sm:order-2">
        <Button
          v-if="treatmentPlan"
          label="下載"
          icon="pi pi-download"
          @click="downloadTreatmentPlan"
          severity="secondary"
          outlined
          size="small"
          class="w-full sm:w-auto text-sm justify-center sm:hidden"
        />

        <Button
          v-if="treatmentPlan"
          label="下載處遇計畫"
          icon="pi pi-download"
          @click="downloadTreatmentPlan"
          severity="secondary"
          outlined
          size="small"
          class="hidden sm:flex w-auto text-sm justify-center"
        />

        <Button
          label="生成計畫"
          icon="pi pi-magic-wand"
          @click="generateTreatmentPlan"
          :disabled="!treatmentValidation.isValid || treatmentStatus === 'generating'"
          :loading="treatmentStatus === 'generating'"
          size="small"
          class="w-full sm:w-auto text-sm justify-center font-medium sm:hidden"
        />

        <Button
          label="生成處遇計畫"
          icon="pi pi-magic-wand"
          @click="generateTreatmentPlan"
          :disabled="!treatmentValidation.isValid || treatmentStatus === 'generating'"
          :loading="treatmentStatus === 'generating'"
          size="small"
          class="hidden sm:flex w-auto text-sm justify-center font-medium"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/stores/useProjectStore'
import { useApiIntegration } from '@/composables/useApiIntegration'
import { useDownload } from '@/composables/useDownload'

// Components
import Card from 'primevue/card'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Checkbox from 'primevue/checkbox'

const projectStore = useProjectStore()
const { generateTreatmentPlan: generateTreatmentPlanAPI } = useApiIntegration()
const { downloadTreatmentPlan: downloadTreatmentPlanFile } = useDownload()

const { treatmentConfig, treatmentPlan, treatmentStatus, treatmentProgress, treatmentValidation } =
  storeToRefs(projectStore)

// 社工服務領域選項
const serviceDomains = [
  { value: 'judicial_correction', name: '司法與矯治' },
  { value: 'economic_assistance', name: '經濟扶助' },
  { value: 'immigrant_indigenous', name: '新(原)住民' },
  { value: 'protection_services', name: '保護服務' },
  { value: 'children_youth', name: '兒童與少年' },
  { value: 'school_education', name: '學校與教育' },
  { value: 'women_family', name: '婦女與家庭' },
  { value: 'medical_related', name: '醫務相關' },
  { value: 'psychological_mental', name: '心理與精神' },
  { value: 'disability', name: '身心障礙' },
  { value: 'elderly_longterm_care', name: '老人與長照' }
]

// Methods
const toggleServiceDomain = (domainValue: string) => {
  projectStore.toggleTreatmentOption('selectedServiceDomains', domainValue)
}

const generateTreatmentPlan = async () => {
  try {
    projectStore.setTreatmentStatus('generating', 0)
    await nextTick()
    await generateTreatmentPlanAPI()
  } catch (error) {
    console.error('生成處遇計畫失敗:', error)
    projectStore.setTreatmentStatus('error', 0)
  }
}

const downloadTreatmentPlan = () => {
  downloadTreatmentPlanFile()
}
</script>

<style scoped>
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

  /* loading 狀態的圖標 */
  :deep(.p-button-loading-icon) {
    font-size: 0.875rem;
  }
}

/* 狀態訊息的響應式調整 */
@media (max-width: 640px) {
  .text-green-600 span,
  .text-orange-600 span {
    line-height: 1.4;
  }
}

/* 確保 loading 按鈕在手機上也有適當的間距 */
@media (max-width: 640px) {
  :deep(.p-button-loading .p-button-label) {
    margin-left: 0.5rem;
  }
}
</style>
