<template>
  <div class="bg-gray-50 font-sans min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Header -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-800 text-left mb-2">
          {{ title }}
        </h1>
        <div class="text-center text-gray-600 text-sm">
          {{ date }}
        </div>
      </div>

      <!-- Content -->
      <div class="bg-white rounded-lg shadow-md p-6 md:p-8">
        <!-- Section 1 -->
        <section class="mb-8">
          <h2 class="text-xl font-bold text-blue-700 mb-4 border-b-2 border-blue-200 pb-2">
            一、適用範圍
          </h2>
          <div class="pl-4 space-y-3">
            <p class="text-gray-700 leading-relaxed">
              1.
              本規範僅適用於國立清華大學王道維教授所領導的AIFR團隊中每一位參與到「社工紀錄輔助系統」(以下稱本系統)開發或維護的人員(以下簡稱為本團隊)。
            </p>
            <p class="text-gray-700 leading-relaxed">
              2. 本規範僅適用於「社工記錄輔助系統」的相關網址與其後端主機的維護方式。
            </p>
            <p class="text-gray-700 leading-relaxed">
              3. 本規範應公開於本系統的網頁並實際執行，以昭公信。
            </p>
          </div>
        </section>

        <!-- Section 2 -->
        <section class="mb-8">
          <h2 class="text-xl font-bold text-blue-700 mb-4 border-b-2 border-blue-200 pb-2">
            二、隱私保護方式與免責聲明
          </h2>
          <div class="pl-4 space-y-3">
            <p class="text-gray-700 leading-relaxed">
              1.
              本系統的測試版目前是公開免費使用，網頁前端不需要任何形式的帳號註冊或登入，最大程度保護使用者的身分隱私。本團隊不得蒐集也不會提供任何使用者資料。
            </p>
            <p class="text-gray-700 leading-relaxed">
              2.
              使用者所上傳到本系統的任何語音或文字資料皆不會在本系統後台保存或備份，僅在使用者端的網路瀏覽器暫存（暫存時間或容量依其廠牌型號而定）。為確保資料安全，使用者可隨時透過清除瀏覽器快取、Cookie
              或其他暫存檔的方式來主動刪除相關資料。本團隊不負任何資料保存責任。
            </p>
            <p class="text-gray-700 leading-relaxed">
              3. 本系統所使用的AI模型(Claude
              API)並無以任何使用者上傳的資料做AI訓練，僅以其原生的語言模型來將這些資料做整理，生成紀錄初稿，且會在一定時間後自動且永久消除，不會做任何其他用途。這個資料處理皆符合美國健康保險可攜性和責任法案（Health
              Insurance Portability and Accountability
              Act）的要求(HIPAA為全球目前最嚴格的健康資料隱私保護法規)。詳情可見本系統的<a
                class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors duration-200"
                href="/securityGuide"
                >「隱私保護</a
              >」分頁與<a
                class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors duration-200"
                href="https://privacy.anthropic.com/en/articles/10015870-what-certifications-has-anthropic-obtained"
                >Claude API的官方資料</a
              >。
            </p>
            <p class="text-gray-700 leading-relaxed">
              4.
              本團隊僅承諾在系統主機安裝必要的安全措施，確保不會保存或外洩使用者所輸入的資料。若因第三方服務（如Claude
              API）之隱私保護或伺服器端問題而發生資料外洩或其他爭議，相關責任由該第三方公司自行承擔，本團隊不負連帶責任。
            </p>
            <p class="text-gray-700 leading-relaxed">
              5.
              本系統所使用的AI模型屬生成式AI，其結果與使用者的輸入資料密切相關且有隨機性，僅適合作為社工訪視紀錄的初稿（包含訪視紀錄、需求評估與處遇計畫）。此初稿仍須經由社工專業判斷與修改，不宜直接作為最終版本。本團隊不保證本系統所生成的初稿是否滿足社工專業需求或是否適用於實際個案。
            </p>
          </div>
        </section>

        <!-- Section 3 -->
        <section class="mb-8">
          <h2 class="text-xl font-bold text-blue-700 mb-4 border-b-2 border-blue-200 pb-2">
            三、本團隊維護本系統程式的規範
          </h2>
          <div class="pl-4 space-y-3">
            <p class="text-gray-700 leading-relaxed">
              1.
              本系統的唯一使用目的是「輔助社工撰寫個案訪視紀錄」。任何與此目的不合的功能增減、程式修改、資料偵測等等操作皆為禁止。
            </p>
            <p class="text-gray-700 leading-relaxed">
              2. 即使符合前節的使用目的來修改此系統程式，本團隊亦應以最小必要的調整為優先考慮。
            </p>
            <p class="text-gray-700 leading-relaxed">
              3.
              本系統的後台僅記錄使用過的流量(包括獨立IP數與API的呼叫次數)，作為本系統運作的觀測指標。本系統並未儲存或保留使用者所輸入或AI回覆的任何語音或文字內容，也不會對這些內容作觀測、分析或統計。
            </p>
            <p class="text-gray-700 leading-relaxed">
              4.
              本系統禁止本團隊內外任何人員(包括團隊領導人)以任何方式檢視本系統使用者所輸入的資料，或是AI所回覆的訊息。
            </p>
          </div>
        </section>

        <!-- Section 4 -->
        <section class="mb-8">
          <h2 class="text-xl font-bold text-blue-700 mb-4 border-b-2 border-blue-200 pb-2">
            四、版本定位與其他單位的合作
          </h2>
          <div class="pl-4 space-y-3">
            <p class="text-gray-700 leading-relaxed">
              1.
              本系統自2025年8月14日公開發布，目前為「測試版」且基於公共化AI的理念與公益性的目的，免費開放外界使用。除了提供第一線社工人員可能的協助以外，也希望藉此蒐集使用的意見回饋來作未來「正式版」的參考。
            </p>
            <p class="text-gray-700 leading-relaxed">
              2.
              目前「測試版」的所有開發費用與API費用皆由清華大學研發處所提供的相關研究計畫支應。並無其他單位或私人企業的資金參與。
            </p>
            <p class="text-gray-700 leading-relaxed">
              3.
              基於AI公共化的理念，未來的「正式版」只要有足夠與穩定的經費支持，仍會以公開免費的方式為優先考慮。屆時如果有運作經費不足的問題，不排除改採收費模式以維持長久營運。但是即使有收費機制也僅用於分擔日常使用與維護成本，不包含開發成本且不以營利為目的。
            </p>
            <p class="text-gray-700 leading-relaxed">
              4.
              未來的「正式版」不排除與社福團體或政府相關部門合作，以提升系統效能、隱私保護、服務範圍或費用分攤等。屆時相關的隱私保護方式可能會有更新。
            </p>
            <p class="text-gray-700 leading-relaxed">
              5.
              未來的「正式版」亦不排除與其他公民營企業合作，提供軟硬體整合的地端模型版本，方便直接部署在機構內部，減少資料外流顧慮與API的使用費。
            </p>
            <p class="text-gray-700 leading-relaxed">
              6.
              基於誠信原則，本團隊會儘量維護此系統的正常運作，但是未來如果因為若干不可抗拒的因素，經過評估後需要停止本系統的服務，應於至少一個月前公告於本系統的網頁。
            </p>
            <p class="text-gray-700 leading-relaxed">
              7. 未來若因為政府對於社工服務或AI使用的頒布相關規定，本規範也會配合同步更新。
            </p>
          </div>
        </section>

        <!-- Footer Info -->
        <div class="mt-8 pt-6 border-t border-gray-200">
          <div class="flex flex-wrap items-center justify-between text-sm text-gray-500">
            <div class="mb-2">
              <span class="font-medium">開發單位：</span>
              國立清華大學 AIFR 團隊
            </div>
          </div>
          <div class="text-center text-xs text-gray-400 mt-4">
            本規範文件版本：初版 | 最後更新：{{ date }}
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-6 flex justify-center space-x-4">
        <button
          @click="printDocument"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
            />
          </svg>
          <span>列印文件</span>
        </button>
        <button
          @click="scrollToTop"
          class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 11l5-5m0 0l5 5m-5-5v12"
            />
          </svg>
          <span>回到頂部</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'PrivacyPolicyPage',
  setup() {
    const title = ref('開發團隊對「社工紀錄輔助系統」的隱私保護規範與單位合作模式')
    const date = ref('2025年8月18日初版')

    const printDocument = () => {
      window.print()
    }

    const scrollToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    onMounted(() => {
      // 添加平滑的載入動畫
      const sections = document.querySelectorAll('section')
      sections.forEach((section, index) => {
        section.style.opacity = '0'
        section.style.transform = 'translateY(20px)'
        setTimeout(() => {
          section.style.transition = 'all 0.6s ease'
          section.style.opacity = '1'
          section.style.transform = 'translateY(0)'
        }, index * 200)
      })
    })

    return {
      title,
      date,
      printDocument,
      scrollToTop
    }
  }
}
</script>

<style scoped>
.font-sans {
  font-family:
    'Microsoft JhengHei',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
}

@media print {
  .bg-gray-50 {
    background-color: white !important;
  }
  button {
    display: none !important;
  }
}
</style>
