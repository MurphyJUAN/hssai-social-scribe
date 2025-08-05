import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UserGuideView from '@/views/UserGuideView.vue'
import SecurityGuideView from '@/views/SecurityGuideView.vue'
import DeveloperTeamView from '@/views/DeveloperTeamView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      alias: '/home',
      component: HomeView
    },
    {
      path: '/userGuide',
      name: 'userGuide',
      alias: '/userGuide',
      component: UserGuideView
    },
    {
      path: '/securityGuide',
      name: 'securityGuide',
      alias: '/securityGuide',
      component: SecurityGuideView
    },
    {
      path: '/devTeam',
      name: 'devTeam',
      alias: '/devTeam',
      component: DeveloperTeamView
    }
  ]
})

export default router
