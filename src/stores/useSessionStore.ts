// stores/useSessionStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { StepType } from '@/types'

interface TabInfo {
  index: number
  key: StepType
  label: string
  icon: string
  enabled: boolean
}

export const useSessionStore = defineStore('session', () => {
  // ==================== Tab 導航狀態 ====================
  const activeTabIndex = ref<number>(0)
  const reportStage = ref<'idle' | 'config' | 'generating' | 'completed'>('idle')
  
  // Tab 定義
  const tabs = ref<TabInfo[]>([
    { 
      index: 0, 
      key: 'transcript', 
      label: '逐字稿', 
      icon: 'pi pi-file-text',
      enabled: true 
    },
    { 
      index: 1, 
      key: 'config', 
      label: '記錄設定', 
      icon: 'pi pi-cog',
      enabled: true
    },
    { 
      index: 2, 
      key: 'draft', 
      label: '記錄初稿', 
      icon: 'pi pi-file-edit',
      enabled: true
    },
    { 
      index: 3, 
      key: 'treatment', 
      label: '處遇計畫設定', 
      icon: 'pi pi-target',
      enabled: true
    }
  ])
  
  // ==================== 導航方法 ====================
  const setActiveTab = (index: number): void => {
    activeTabIndex.value = index
  }
  
  const setReportStage = (stage: 'idle' | 'config' | 'generating' | 'completed'): void => {
    reportStage.value = stage
  }
  
  const nextTab = (): void => {
    if (activeTabIndex.value < tabs.value.length - 1) {
      activeTabIndex.value++
    }
  }
  
  const prevTab = (): void => {
    if (activeTabIndex.value > 0) {
      activeTabIndex.value--
    }
  }
  
  const goToTab = (tabKey: StepType): void => {
    const tab = tabs.value.find(t => t.key === tabKey)
    if (tab) {
      activeTabIndex.value = tab.index
    }
  }
  
  // ==================== Computed ====================
  const currentTab = computed((): TabInfo | undefined => {
    return tabs.value[activeTabIndex.value]
  })
  
  const canGoNext = computed((): boolean => {
    return activeTabIndex.value < tabs.value.length - 1
  })
  
  const canGoPrev = computed((): boolean => {
    return activeTabIndex.value > 0
  })
  
  return {
    // State
    activeTabIndex,
    reportStage,
    tabs,
    
    // Computed
    currentTab,
    canGoNext,
    canGoPrev,
    
    // Actions
    setActiveTab,
    setReportStage,
    nextTab,
    prevTab,
    goToTab
  }
})