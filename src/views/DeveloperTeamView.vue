<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- 頁面標題 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-4 flex items-center justify-center">
          <i class="pi pi-users mr-3 text-blue-600"></i>
          開發團隊
        </h1>
        <p class="text-lg text-gray-600">AI 社工訪視記錄系統背後的開發團隊</p>
      </div>

      <div class="space-y-8">
        <!-- 資工技術團隊 -->
        <div class="p-6 border-l-4 border-l-blue-500 bg-blue-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-6 text-blue-700 flex items-center">
            <i class="pi pi-desktop mr-3"></i>資工技術
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 羅偉哲 -->
            <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-user text-blue-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-blue-700">羅偉哲</h3>
                  <p class="text-base text-gray-600">技術開發</p>
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-graduation-cap text-blue-500 mr-3"></i>
                  <span>清華大學物理系</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-code text-green-500 mr-3"></i>
                  <span>前端開發 & 系統架構</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-cog text-purple-500 mr-3"></i>
                  <span>AI 整合 & 使用者介面設計</span>
                </div>
              </div>
            </div>

            <!-- 阮羿寧 -->
            <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-user text-blue-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-blue-700">阮羿寧</h3>
                  <p class="text-base text-gray-600">技術開發</p>
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-graduation-cap text-blue-500 mr-3"></i>
                  <span>清華大學人文社會AI應用與發展研究中心</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-brain text-green-500 mr-3"></i>
                  <span>AI 應用研究 & 資料分析</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-chart-line text-purple-500 mr-3"></i>
                  <span>機器學習 & 自然語言處理</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 指導教授 -->
        <div class="p-6 border-l-4 border-l-green-500 bg-green-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-6 text-green-700 flex items-center">
            <i class="pi pi-star mr-3"></i>指導教授
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 施睿誼教授 -->
            <div class="bg-white p-6 rounded-lg border border-green-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-user-graduate text-green-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-green-700">施睿誼 教授</h3>
                  <!-- <p class="text-base text-gray-600">社工專業指導</p> -->
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-building text-green-500 mr-3"></i>
                  <span>亞洲大學社會工作學系</span>
                </div>
                <!-- <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-heart text-red-500 mr-3"></i>
                  <span>社工實務專業指導</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-clipboard text-blue-500 mr-3"></i>
                  <span>記錄格式與倫理標準</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-users text-purple-500 mr-3"></i>
                  <span>使用者需求分析</span>
                </div> -->
              </div>
            </div>

            <!-- 王道維教授 -->
            <div class="bg-white p-6 rounded-lg border border-green-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-user-graduate text-green-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-green-700">王道維 教授</h3>
                  <!-- <p class="text-base text-gray-600">AI 技術指導</p> -->
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-building text-green-500 mr-3"></i>
                  <span>國立清華大學物理系</span>
                </div>
                <!-- <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-sitemap text-orange-500 mr-3"></i>
                  <span>人文社會AI應用與發展研究中心</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-cog text-blue-500 mr-3"></i>
                  <span>AI 技術架構指導</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-shield text-purple-500 mr-3"></i>
                  <span>資料安全與倫理監督</span>
                </div> -->
              </div>
            </div>
          </div>
        </div>

        <!-- 合作單位 -->
        <div class="p-6 border-l-4 border-l-orange-500 bg-orange-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-6 text-orange-700 flex items-center">
            <i class="pi pi-handshake mr-3"></i>合作單位
            <span class="ml-3 text-sm bg-orange-100 text-orange-700 px-3 py-1 rounded"
              >持續增加中</span
            >
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 士林地方法院家事服務中心 -->
            <div class="bg-white p-6 rounded-lg border border-orange-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-building-columns text-orange-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-lg font-bold text-orange-700">士林地方法院</h3>
                  <p class="text-base text-gray-600">家事服務中心</p>
                </div>
              </div>

              <!-- <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-home text-blue-500 mr-3"></i>
                  <span>家事案件處理</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-users text-green-500 mr-3"></i>
                  <span>家庭關係評估</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-file-edit text-purple-500 mr-3"></i>
                  <span>專業記錄撰寫</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-heart text-red-500 mr-3"></i>
                  <span>兒童最佳利益評估</span>
                </div>
              </div> -->
            </div>

            <!-- 桃園市第三區早期療育發展中心 -->
            <div class="bg-white p-6 rounded-lg border border-orange-200 shadow-sm">
              <div class="flex items-center mb-4">
                <div
                  class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mr-4"
                >
                  <i class="pi pi-heart text-orange-600 text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-lg font-bold text-orange-700">桃園市第三區</h3>
                  <p class="text-base text-gray-600">早期療育發展中心</p>
                </div>
              </div>

              <!-- <div class="space-y-3">
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-child text-blue-500 mr-3"></i>
                  <span>兒童發展評估</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-chart-line text-green-500 mr-3"></i>
                  <span>療育進度追蹤</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-users text-purple-500 mr-3"></i>
                  <span>家庭支持服務</span>
                </div>
                <div class="flex items-center text-sm text-gray-700">
                  <i class="pi pi-clipboard text-red-500 mr-3"></i>
                  <span>個別化服務計畫</span>
                </div>
              </div> -->
            </div>
          </div>

          <!-- 合作說明 -->
          <div class="mt-6 p-4 bg-orange-100 rounded-lg">
            <div class="flex items-center text-base text-orange-700">
              <i class="pi pi-info-circle mr-3"></i>
              <span>我們持續與更多專業機構建立合作關係，共同推動社工數位化發展</span>
            </div>
          </div>
        </div>

        <!-- 團隊願景 -->
        <!-- <div class="p-6 border-l-4 border-l-purple-500 bg-purple-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-6 text-purple-700 flex items-center">
            <i class="pi pi-eye mr-3"></i>團隊願景
          </h2>
          
          <div class="bg-white p-6 rounded-lg border border-purple-200 shadow-sm">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="text-center">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i class="pi pi-lightbulb text-purple-600 text-2xl"></i>
                </div>
                <h3 class="font-bold text-lg text-purple-700 mb-2">創新科技</h3>
                <p class="text-sm text-gray-700">
                  運用最新的 AI 技術，為社工專業帶來革命性的工作方式
                </p>
              </div>
              
              <div class="text-center">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i class="pi pi-heart text-purple-600 text-2xl"></i>
                </div>
                <h3 class="font-bold text-lg text-purple-700 mb-2">專業服務</h3>
                <p class="text-sm text-gray-700">
                  讓社工有更多時間專注於案主服務，提升服務品質
                </p>
              </div>
              
              <div class="text-center">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i class="pi pi-shield text-purple-600 text-2xl"></i>
                </div>
                <h3 class="font-bold text-lg text-purple-700 mb-2">安全可靠</h3>
                <p class="text-sm text-gray-700">
                  確保最高等級的資料安全，符合專業倫理要求
                </p>
              </div>
            </div>
            
            <div class="mt-6 p-4 bg-purple-100 rounded-lg text-center">
              <p class="text-base text-purple-700 font-medium">
                「讓科技成為社工專業的最佳夥伴，共同為案主創造更好的服務體驗」
              </p>
            </div>
          </div>
        </div> -->

        <!-- 聯絡資訊 -->
        <div class="p-6 border-l-4 border-l-cyan-500 bg-cyan-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-6 text-cyan-700 flex items-center">
            <i class="pi pi-envelope mr-3"></i>聯絡我們
          </h2>

          <div class="bg-white p-6 rounded-lg border border-cyan-200 shadow-sm">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="font-bold text-lg text-cyan-700 mb-4">技術支援</h3>
                <div class="space-y-3">
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-question-circle text-blue-500 mr-3"></i>
                    <span>系統使用問題</span>
                  </div>
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-cog text-green-500 mr-3"></i>
                    <span>功能建議與回饋</span>
                  </div>
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-exclamation-triangle text-orange-500 mr-3"></i>
                    <span>技術問題回報</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 class="font-bold text-lg text-cyan-700 mb-4">合作洽詢</h3>
                <div class="space-y-3">
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-handshake text-purple-500 mr-3"></i>
                    <span>機構合作機會</span>
                  </div>
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-graduation-cap text-blue-500 mr-3"></i>
                    <span>學術研究合作</span>
                  </div>
                  <div class="flex items-center text-sm text-gray-700">
                    <i class="pi pi-users text-green-500 mr-3"></i>
                    <span>專業交流活動</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-6 p-4 bg-cyan-100 rounded-lg text-center">
              <p class="text-base text-cyan-700">
                歡迎各界專業人士與我們聯繫，共同推動社工領域的數位轉型
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 返回按鈕 -->
      <!-- <div class="flex justify-center mt-12">
        <button 
          @click="$router.go(-1)" 
          class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg flex items-center text-lg font-medium transition-colors duration-200"
        >
          <i class="pi pi-arrow-left mr-2"></i>
          返回上一頁
        </button>
      </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
// 如果需要使用 router，確保已經導入
// import { useRouter } from 'vue-router'
// const router = useRouter()
</script>

<style scoped>
/* 可以根據需要添加額外的樣式 */
.container {
  max-width: 1200px;
}
</style>
