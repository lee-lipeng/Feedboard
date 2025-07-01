import './assets/main.css'

import {createApp} from 'vue'
import {createPinia} from 'pinia'
import App from './App.vue'
import router from './router'
import {useAuthStore} from './stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 尝试在应用加载时获取用户信息
const authStore = useAuthStore()
authStore.fetchUser().catch(error => {
    console.error('启动时获取用户信息失败:', error)
    authStore.logout()
})

app.mount('#app')
