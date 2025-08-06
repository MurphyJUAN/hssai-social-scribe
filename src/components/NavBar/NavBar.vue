<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import NavLink from '@/components/NavBar/NavLink.vue'

const navbarLinks = [
  {
    to: '/',
    name: '首頁',
    children: []
  },
  {
    to: '/userGuide',
    name: '使用說明',
    children: []
  },
  {
    to: '/securityGuide',
    name: '隱私性說明',
    children: []
  },
  {
    to: '/devTeam',
    name: '開發團隊',
    children: []
  }
]

const menuOpen = ref<Boolean>(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const closeMenu = (event: MouseEvent) => {
  // to close dropdown on click
  ;(event.target as HTMLElement).blur()
  menuOpen.value = false
}
</script>

<template>
  <nav class="bg-white fixed w-full z-20 top-0 left-0 border-b border-gray-200">
    <div class="max-w-screen-2xl flex flex-wrap items-center justify-between mx-auto p-4">
      <RouterLink to="/" class="flex items-center space-x-3">
        <!-- Insert logo here -->
        <!-- <img src="" class="h-8" alt="Logo" /> -->
        <span class="self-center text-xl font-semibold whitespace-nowrap">
          AI社工訪視紀錄系統
        </span>
      </RouterLink>
      <!-- Hamburger Menu -->
      <div class="flex md:order-2 space-x-3 md:space-x-0">
        <button
          type="button"
          class="inline-flex items-center p-2 w-8 h-8 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
          aria-controls="navbar-sticky"
          aria-expanded="false"
          @click="toggleMenu"
        >
          <span class="sr-only">Open main menu</span>
          <svg
            class="w-5 h-5"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 17 14"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M1 1h15M1 7h15M1 13h15"
            />
          </svg>
        </button>
      </div>
      <!-- Navigations -->
      <div
        :class="
          menuOpen
            ? 'items-center w-full md:flex md:order-2 md:w-fit'
            : 'items-center hidden w-full md:flex md:order-2 md:w-fit'
        "
      >
        <ul
          class="flex flex-col p-4 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:w-full md:justify-center md:mt-0 md:p-0 md:flex-row md:border-0 md:text-sm md:space-x-4 md:bg-white lg:text-base lg:space-x-6 xl:space-x-8"
        >
          <li v-for="(link, index) in navbarLinks" :key="index">
            <NavLink
              :to="link.to"
              :closeMenu="closeMenu"
              :children="link.children ? link.children : undefined"
            >
              {{ link.name }}
            </NavLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style lang="scss" scoped></style>
