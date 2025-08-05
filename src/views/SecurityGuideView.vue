
<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      
      <!-- 頁面標題 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-4 flex items-center justify-center">
          <i class="pi pi-shield mr-3 text-blue-600"></i>
          Claude API 安全性說明
        </h1>
        <p class="text-lg text-gray-600">醫療級隱私保護，專業級安全保障</p>
      </div>

      <div class="space-y-8">
        
        <!-- 安全認證等級 -->
        <div class="p-6 border-l-4 border-l-blue-500 bg-blue-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-4 text-blue-700 flex items-center">
            <i class="pi pi-verified mr-3"></i>安全認證等級
          </h2>
          <p class="text-base text-blue-600 mb-6">Claude API 擁有業界最高等級的安全認證組合</p>
          
          <div class="space-y-6">
            <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
              <div class="flex items-center mb-4">
                <i class="pi pi-hospital text-red-600 mr-3 text-xl"></i>
                <span class="font-semibold text-xl text-blue-700">HIPAA 認證</span>
                <span class="ml-3 text-sm bg-red-100 text-red-700 px-3 py-1 rounded">最重要</span>
              </div>
              <p class="text-base text-gray-700 mb-4">
                <strong>HIPAA 是什麼：</strong>美國健康保險可攜性和責任法案（Health Insurance Portability and Accountability Act），是全球最嚴格的健康資料隱私保護法規
              </p>
              <p class="text-base text-blue-700 mb-4 bg-blue-50 p-4 rounded">
                <strong>🏥 涵蓋範圍：</strong>不只是醫療資料，還包括心理健康、家庭狀況、社會服務等所有與健康相關的個人資訊
              </p>
              <p class="text-base text-gray-700 mb-4">
                <strong>對社工的意義：</strong>社工處理的案主資料經常涉及健康、心理、家庭、兒童保護等敏感資訊，HIPAA 確保這些資料受到醫療等級的最高保護
              </p>
              <p class="text-base text-green-700 mb-4 bg-green-50 p-4 rounded">
                <strong>🛡️ 具體保護措施：</strong>
                <br>• 最低必要原則：只能存取完成工作所需的最少資料
                <br>• 技術防護：加密、存取控制、使用者驗證
                <br>• 實體防護：安全的資料中心、環境控制
                <br>• 管理防護：員工訓練、政策制定、事件回應
              </p>
              <p class="text-base text-green-700">
                <strong>具體保障：</strong>醫療級傳輸加密、嚴格存取控制、完整稽核追蹤
              </p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
                <div class="flex items-center mb-4">
                  <i class="pi pi-shield text-green-600 mr-3 text-lg"></i>
                  <span class="font-semibold text-lg text-blue-700">SOC 2 Type 2</span>
                </div>
                <p class="text-sm text-gray-700 mb-3">
                  <strong>這是什麼：</strong>獨立第三方持續一年以上的安全性稽核認證
                </p>
                <p class="text-sm text-gray-700">
                  <strong>保障內容：</strong>安全性、可用性、處理完整性、機密性、隱私保護五大面向
                </p>
              </div>
              
              <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
                <div class="flex items-center mb-4">
                  <i class="pi pi-globe text-green-600 mr-3 text-lg"></i>
                  <span class="font-semibold text-lg text-blue-700">ISO 27001</span>
                </div>
                <p class="text-sm text-gray-700 mb-3">
                  <strong>這是什麼：</strong>國際標準組織制定的資訊安全管理標準
                </p>
                <p class="text-sm text-gray-700">
                  <strong>保障內容：</strong>全面的安全政策、風險管理、事件回應、員工訓練
                </p>
              </div>
              
              <div class="bg-white p-6 rounded-lg border border-blue-200 shadow-sm">
                <div class="flex items-center mb-4">
                  <i class="pi pi-cog text-green-600 mr-3 text-lg"></i>
                  <span class="font-semibold text-lg text-blue-700">ISO 42001</span>
                </div>
                <p class="text-sm text-gray-700 mb-3">
                  <strong>這是什麼：</strong>專門針對 AI 系統的管理認證（2023年新標準）
                </p>
                <p class="text-sm text-gray-700">
                  <strong>保障內容：</strong>AI 系統的負責任開發、部署、監控和改進
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 核心安全承諾 -->
        <div class="p-6 border-l-4 border-l-green-500 bg-green-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-4 text-green-700 flex items-center">
            <i class="pi pi-lock mr-3"></i>核心安全承諾
          </h2>
          
          <div class="space-y-4">
            <div class="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm">
              <i class="pi pi-shield text-blue-500 mt-1 flex-shrink-0 text-xl"></i>
              <div>
                <div class="font-semibold text-base text-green-700">醫療級資料保護</div>
                <p class="text-sm text-gray-600 mt-2">
                  提供醫療等級的資料安全保護，符合最嚴格的隱私標準
                </p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm">
              <i class="pi pi-eye-slash text-purple-500 mt-1 flex-shrink-0 text-xl"></i>
              <div>
                <div class="font-semibold text-base text-green-700">員工存取控制</div>
                <p class="text-sm text-gray-600 mt-2">
                  未經授權的員工無法讀取您的對話內容，僅信任與安全團隊按需審查
                </p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm">
              <i class="pi pi-clock text-blue-500 mt-1 flex-shrink-0 text-xl"></i>
              <div>
                <div class="font-semibold text-base text-green-700">即時處理</div>
                <p class="text-sm text-gray-600 mt-2">
                  資料僅在處理期間存在於記憶體中，處理完成後立即清除
                </p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm">
              <i class="pi pi-shield text-purple-500 mt-1 flex-shrink-0 text-xl"></i>
              <div>
                <div class="font-semibold text-base text-green-700">端到端加密</div>
                <p class="text-sm text-gray-600 mt-2">
                  所有資料傳輸都經過 TLS 1.3 加密，確保傳輸過程完全安全
                </p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 bg-white p-4 rounded-lg shadow-sm">
              <i class="pi pi-shield text-orange-500 mt-1 flex-shrink-0 text-xl"></i>
              <div>
                <div class="font-semibold text-base text-green-700">完整稽核追蹤</div>
                <p class="text-sm text-gray-600 mt-2">
                  所有資料處理活動都有完整的稽核記錄，確保符合法規要求
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 與其他 AI 服務比較 -->
        <div class="p-6 border-l-4 border-l-purple-500 bg-purple-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-4 text-purple-700 flex items-center">
            <i class="pi pi-chart-bar mr-3"></i>安全性比較
          </h2>
          
          <div class="overflow-x-auto">
            <table class="w-full text-sm border border-gray-200 rounded-lg bg-white">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left">服務</th>
                  <th class="px-4 py-3 text-center">HIPAA</th>
                  <th class="px-4 py-3 text-center">SOC 2</th>
                  <th class="px-4 py-3 text-center">ISO 27001</th>
                  <th class="px-4 py-3 text-center">推薦程度</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr class="bg-purple-50">
                  <td class="px-4 py-3 font-semibold">Claude API</td>
                  <td class="px-4 py-3 text-center text-green-600">✅</td>
                  <td class="px-4 py-3 text-center text-green-600">✅</td>
                  <td class="px-4 py-3 text-center text-green-600">✅</td>
                  <td class="px-4 py-3 text-center">
                    <span class="text-orange-600">中等</span>
                    <div class="text-xs text-gray-500">可能被掃描</div>
                  </td>
                  <td class="px-4 py-3 text-center">⭐⭐</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="mt-6 p-6 bg-blue-100 rounded-lg border border-blue-300">
            <h3 class="font-semibold text-base text-blue-700 mb-4 flex items-center">
              <i class="pi pi-info-circle mr-2"></i>重要澄清說明
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="font-semibold text-sm text-blue-600 mb-3">🔐 Claude API 醫療級安全</h4>
                <ul class="text-sm text-blue-700 space-y-2">
                  <li>• 提供醫療等級的資料安全保護</li>
                  <li>• 具備 <strong>HIPAA 認證</strong>，達到醫療等級保護</li>
                  <li>• 員工無法讀取您的對話內容</li>
                  <li>• 符合最嚴格的醫療隱私標準</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold text-sm text-blue-600 mb-3">📋 其他工具比較</h4>
                <ul class="text-sm text-blue-700 space-y-2">
                  <li>• LINE 端到端加密很好，但伺服器永久保存</li>
                  <li>• Gmail 會主動掃描內容用於廣告</li>
                  <li>• 雲端硬碟較安全但仍可能被政策掃描</li>
                  <li>• 整體而言 Claude 仍是相對最安全的選擇</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="mt-6 p-4 bg-green-100 rounded-lg">
            <div class="flex items-center text-base text-green-700">
              <i class="pi pi-check-circle mr-3"></i>
              <span><strong>結論：</strong>即使考量到這些限制，Claude 仍是目前處理敏感資料相對最安全的 AI 工具</span>
            </div>
          </div>
        </div>

        <!-- 常見安全疑問 -->
        <div class="p-6 border-l-4 border-l-pink-500 bg-pink-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-4 text-pink-700 flex items-center">
            <i class="pi pi-question-circle mr-3"></i>常見安全疑問
          </h2>
          
          <div class="space-y-6">
            <div class="bg-white p-6 rounded-lg border border-pink-200 shadow-sm">
              <h3 class="font-semibold text-base text-pink-600 mb-3">❓ 資料會被洩露嗎？</h3>
              <p class="text-sm text-gray-700">
                <strong>答：</strong>不會。HIPAA 醫療級認證 + 端到端加密 + 嚴格存取控制，安全等級比 email 和雲端硬碟都高。
              </p>
            </div>
            
            <div class="bg-white p-6 rounded-lg border border-pink-200 shadow-sm">
              <h3 class="font-semibold text-base text-pink-600 mb-3">❓ 會被用來訓練AI嗎？</h3>
              <p class="text-sm text-gray-700">
                <strong>答：</strong>Claude 有嚴格的資料使用限制，提供醫療級的隱私保護，資料處理符合最高安全標準。
              </p>
            </div>
            
            <div class="bg-white p-6 rounded-lg border border-pink-200 shadow-sm">
              <h3 class="font-semibold text-base text-pink-600 mb-3">❓ 比其他AI安全嗎？</h3>
              <p class="text-sm text-gray-700">
                <strong>答：</strong>是的。Claude API是唯一有HIPAA認證的主流AI服務，安全等級最高。
              </p>
            </div>
            
            <div class="bg-white p-6 rounded-lg border border-pink-200 shadow-sm">
              <h3 class="font-semibold text-base text-pink-600 mb-3">❓ 機構會接受嗎？</h3>
              <p class="text-sm text-gray-700">
                <strong>答：</strong>很可能。HIPAA認證意味著符合醫療機構的安全標準，可提供給IT部門評估。
              </p>
            </div>
          </div>
        </div>

        <!-- 最終建議 -->
        <div class="p-6 border-l-4 border-l-emerald-500 bg-emerald-50 rounded-r-lg shadow-sm">
          <h2 class="text-2xl font-bold mb-4 text-emerald-700 flex items-center">
            <i class="pi pi-thumbs-up mr-3"></i>使用建議總結
          </h2>
          
          <div class="bg-white p-6 rounded-lg border border-emerald-200 shadow-sm">
            <div class="flex items-start space-x-4 mb-6">
              <i class="pi pi-star-fill text-yellow-500 text-2xl mt-1"></i>
              <div>
                <h3 class="font-bold text-xl text-emerald-700">Claude API 安全等級：⭐⭐⭐⭐⭐</h3>
                <p class="text-base text-gray-700 mt-2">
                  提供目前可取得的最高AI安全保護，完全適合社工專業安全使用
                </p>
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <h4 class="font-semibold text-base text-emerald-600 mb-3">🚀 立即可用</h4>
                <ul class="text-sm text-gray-700 space-y-2">
                  <li>• 適度去識別化後安全使用</li>
                  <li>• 從簡單記錄開始嘗試</li>
                  <li>• 保持專業判斷優先</li>
                  <li>• 與督導討論重要案件</li>
                </ul>
              </div>
              
              <div>
                <h4 class="font-semibold text-base text-emerald-600 mb-3">📋 核心原則</h4>
                <ul class="text-sm text-gray-700 space-y-2">
                  <li>• 技術上：比現有工具都安全</li>
                  <li>• 法規上：符合最嚴格標準</li>
                  <li>• 專業上：輔助不取代判斷</li>
                  <li>• 實務上：簡單易用高效</li>
                </ul>
              </div>
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