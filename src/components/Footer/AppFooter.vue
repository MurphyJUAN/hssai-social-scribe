<script setup lang="ts"></script>
<template>
  <footer class="bg-white border-t">
    <div class="mx-auto w-full max-w-screen-xl p-4 py-6 lg:py-8">
      <div class="flex flex-col items-center space-y-4 lg:flex-row lg:justify-between lg:space-y-0">
        <!-- left (原本的 right) -->
        <div class="text-center text-sm text-gray-500 sm:flex sm:items-center">
          <div>
            聯絡我們：<a href="mailto:aifr.general@gmail.com" class="hover:underline"
              >aifr.general@gmail.com</a
            >
          </div>
        </div>
        <!-- right (原本的 left) -->
        <div class="">
          <div
            class="flex flex-col items-center space-y-4 sm:space-y-0 sm:flex-row sm:items-center sm:justify-start sm:space-x-4"
          >
            <a href="https://www.nthu.edu.tw/" target="_blank">
              <img src="@/assets/logo_nthu.png" class="h-12" alt="NTHU Logo" />
            </a>
            <a href="https://nthuhssai.site.nthu.edu.tw/" target="_blank">
              <img src="@/assets/logo_hssai.png" class="h-12" alt="HSSAI Logo" />
            </a>
            <div class="text-center text-sm text-gray-500 sm:text-left text-nowrap">
              <a class="hover:underline" href="https://nthuhssai.site.nthu.edu.tw/" target="_blank"
                >國立清華大學 人文社會AI應用與發展研究中心</a
              >
              <br />
              <a class="hover:underline" href="http://www.phys.nthu.edu.tw/~aicmt/" target="_blank">
                國立清華大學 AIFR人工智慧與基礎研究群</a
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
<style scoped></style>
