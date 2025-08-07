<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 標題區域 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">流量分析儀表板</h1>
        <p class="text-gray-600">查看 API 使用情況和性能統計</p>
      </div>

      <!-- 日期選擇區域 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">開始日期</label>
            <Calendar
              v-model="startDate"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-48"
              placeholder="選擇開始日期"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">結束日期</label>
            <Calendar
              v-model="endDate"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-48"
              placeholder="選擇結束日期"
            />
          </div>
          <div class="flex gap-2 mt-6">
            <Button
              @click="loadData"
              :loading="loading"
              :disabled="!startDate || !endDate"
              icon="pi pi-search"
              label="查詢"
              class="bg-blue-500 hover:bg-blue-600"
            />
            <Button @click="setQuickRange('today')" label="今天" severity="secondary" outlined />
            <Button @click="setQuickRange('week')" label="近7天" severity="secondary" outlined />
            <Button @click="setQuickRange('month')" label="近30天" severity="secondary" outlined />
          </div>
        </div>
      </div>

      <!-- 載入中 -->
      <div v-if="loading" class="flex justify-center py-12">
        <ProgressSpinner />
      </div>

      <!-- 統計卡片 -->
      <div
        v-else-if="summaryStats"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">總請求數</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ summaryStats.totalRequests.toLocaleString() }}
              </p>
            </div>
            <div class="p-3 bg-blue-100 rounded-full">
              <i class="pi pi-chart-line text-blue-600 text-xl"></i>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">獨立IP數</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ summaryStats.distinctIps.toLocaleString() }}
              </p>
            </div>
            <div class="p-3 bg-green-100 rounded-full">
              <i class="pi pi-users text-green-600 text-xl"></i>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">成功率</p>
              <p class="text-2xl font-bold text-gray-900">{{ summaryStats.successRate }}%</p>
            </div>
            <div class="p-3 bg-yellow-100 rounded-full">
              <i class="pi pi-check-circle text-yellow-600 text-xl"></i>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">平均處理時間</p>
              <p class="text-2xl font-bold text-gray-900">{{ summaryStats.avgProcessingTime }}ms</p>
            </div>
            <div class="p-3 bg-red-100 rounded-full">
              <i class="pi pi-clock text-red-600 text-xl"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 圖表區域 -->
      <div v-if="chartData.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 每日請求趨勢圖 -->
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">每日請求趨勢</h3>
          <Chart type="line" :data="dailyRequestsChart" :options="chartOptions" class="h-64" />
        </div>

        <!-- 每日獨立IP趨勢圖 -->
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">每日獨立IP趨勢</h3>
          <Chart type="line" :data="dailyIpsChart" :options="chartOptions" class="h-64" />
        </div>

        <!-- API端點使用分佈 -->
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">API端點使用分佈</h3>
          <Chart
            type="doughnut"
            :data="apiEndpointsChart"
            :options="doughnutOptions"
            class="h-64"
          />
        </div>

        <!-- 成功率趨勢 -->
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">成功率趨勢</h3>
          <Chart
            type="line"
            :data="successRateChart"
            :options="percentageChartOptions"
            class="h-64"
          />
        </div>
      </div>

      <!-- 詳細數據表格 -->
      <div v-if="chartData.length > 0" class="bg-white rounded-lg shadow-md">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">詳細數據</h3>
        </div>
        <DataTable
          :value="chartData"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 25, 50]"
          class="p-datatable-sm"
          responsiveLayout="stack"
          :loading="loading"
        >
          <Column field="date" header="日期" sortable>
            <template #body="slotProps">
              {{ formatDate(slotProps.data.date) }}
            </template>
          </Column>
          <Column field="total_requests" header="總請求數" sortable>
            <template #body="slotProps">
              {{ slotProps.data.total_requests.toLocaleString() }}
            </template>
          </Column>
          <Column field="distinct_ips" header="獨立IP" sortable>
            <template #body="slotProps">
              {{ slotProps.data.distinct_ips.toLocaleString() }}
            </template>
          </Column>
          <Column field="transcribe_count" header="轉錄API" sortable>
            <template #body="slotProps">
              {{ slotProps.data.transcribe_count.toLocaleString() }}
            </template>
          </Column>
          <Column field="report_count" header="報告API" sortable>
            <template #body="slotProps">
              {{ slotProps.data.report_count.toLocaleString() }}
            </template>
          </Column>
          <Column field="treatment_count" header="治療計劃API" sortable>
            <template #body="slotProps">
              {{ slotProps.data.treatment_count.toLocaleString() }}
            </template>
          </Column>
          <Column field="success_rate" header="成功率" sortable>
            <template #body="slotProps">
              <Badge
                :value="`${slotProps.data.success_rate}%`"
                :severity="
                  slotProps.data.success_rate >= 95
                    ? 'success'
                    : slotProps.data.success_rate >= 85
                      ? 'warning'
                      : 'danger'
                "
              />
            </template>
          </Column>
          <Column field="avg_processing_time" header="平均處理時間" sortable>
            <template #body="slotProps"> {{ slotProps.data.avg_processing_time }}ms </template>
          </Column>
          <Column field="total_file_size" header="總文件大小" sortable>
            <template #body="slotProps">
              {{ formatFileSize(slotProps.data.total_file_size) }}
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- 錯誤提示 -->
      <Message v-if="error" severity="error" :closable="false">
        {{ error }}
      </Message>

      <!-- 無數據提示 -->
      <div v-if="!loading && chartData.length === 0 && !error" class="text-center py-12">
        <i class="pi pi-chart-line text-6xl text-gray-300 mb-4"></i>
        <h3 class="text-xl font-semibold text-gray-600 mb-2">暫無數據</h3>
        <p class="text-gray-500">請選擇日期範圍並點擊查詢按鈕</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import Calendar from 'primevue/calendar'
import Button from 'primevue/button'
import Chart from 'primevue/chart'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'

const analyticsStore = useAnalyticsStore()

// 響應式數據
const startDate = ref<Date | null>(null)
const endDate = ref<Date | null>(null)
const loading = ref(false)
const error = ref('')

// 計算屬性
const chartData = computed(() => analyticsStore.trafficData)

const summaryStats = computed(() => {
  if (!chartData.value.length) return null

  const totalRequests = chartData.value.reduce((sum, day) => sum + day.total_requests, 0)
  const totalDistinctIps = Math.max(...chartData.value.map((day) => day.distinct_ips))
  const totalErrors = chartData.value.reduce((sum, day) => sum + day.error_count, 0)
  const successRate =
    totalRequests > 0 ? Math.round(((totalRequests - totalErrors) / totalRequests) * 100) : 0
  const avgProcessingTime = Math.round(
    chartData.value.reduce((sum, day) => sum + day.avg_processing_time, 0) / chartData.value.length
  )

  return {
    totalRequests,
    distinctIps: totalDistinctIps,
    successRate,
    avgProcessingTime
  }
})

// 圖表數據
const dailyRequestsChart = computed(() => ({
  labels: chartData.value.map((d) => formatDate(d.date)),
  datasets: [
    {
      label: '每日請求數',
      data: chartData.value.map((d) => d.total_requests),
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    }
  ]
}))

const dailyIpsChart = computed(() => ({
  labels: chartData.value.map((d) => formatDate(d.date)),
  datasets: [
    {
      label: '每日獨立IP',
      data: chartData.value.map((d) => d.distinct_ips),
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4,
      fill: true
    }
  ]
}))

const apiEndpointsChart = computed(() => {
  const totalTranscribe = chartData.value.reduce((sum, day) => sum + day.transcribe_count, 0)
  const totalReport = chartData.value.reduce((sum, day) => sum + day.report_count, 0)
  const totalTreatment = chartData.value.reduce((sum, day) => sum + day.treatment_count, 0)

  return {
    labels: ['轉錄API', '報告API', '治療計劃API'],
    datasets: [
      {
        data: [totalTranscribe, totalReport, totalTreatment],
        backgroundColor: ['#3B82F6', '#10B981', '#F59E0B']
      }
    ]
  }
})

const successRateChart = computed(() => ({
  labels: chartData.value.map((d) => formatDate(d.date)),
  datasets: [
    {
      label: '成功率 (%)',
      data: chartData.value.map((d) => d.success_rate),
      borderColor: '#EF4444',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      tension: 0.4,
      fill: true
    }
  ]
}))

// 圖表配置
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const percentageChartOptions = {
  ...chartOptions,
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: function (value: number) {
          return value + '%'
        }
      }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

// 方法
const loadData = async () => {
  if (!startDate.value || !endDate.value) {
    error.value = '請選擇開始和結束日期'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const start = formatDateForAPI(startDate.value)
    const end = formatDateForAPI(endDate.value)
    await analyticsStore.fetchTrafficData(start, end)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入數據時發生錯誤'
  } finally {
    loading.value = false
  }
}

const setQuickRange = (range: string) => {
  const today = new Date()
  const end = new Date(today)

  switch (range) {
    case 'today':
      startDate.value = new Date(today)
      endDate.value = new Date(today)
      break
    case 'week':
      startDate.value = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      endDate.value = end
      break
    case 'month':
      startDate.value = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      endDate.value = end
      break
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateForAPI = (date: Date) => {
  return date.toISOString().split('T')[0]
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// 初始化
onMounted(() => {
  setQuickRange('week')
})
</script>
