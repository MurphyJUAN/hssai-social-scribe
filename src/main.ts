import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import Tooltip from 'primevue/tooltip'

import Lara from '@/primevue-presets/lara'
import 'primeicons/primeicons.css'
import './style.css'

const pinia = createPinia()
pinia.use(
  createPersistedState({
    storage: localStorage,
    debug: true // 開發環境可以開啟
  })
)

const app = createApp(App)
app.directive('tooltip', Tooltip)
app.use(pinia)
app.use(router)
app.use(PrimeVue, {
  unstyled: true,
  pt: Lara
})
app.use(ToastService)
app.use(ToastService)
app.use(ConfirmationService)

app.mount('#app')
