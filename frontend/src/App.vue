<script setup lang="ts">
import { RouterView } from 'vue-router';
import { usePreferencesStore } from '@/stores/preferences';
import { useAuthStore } from '@/stores/auth';
import { onMounted, watch } from 'vue';
import { initializeAutoRefresh, stopAutoRefresh } from './utils/autoRefresh';

const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();

// 统一处理认证状态变化
const handleAuthChange = (token: string | null) => {
  if (token) {
    // 用户已登录或刚刚登录
    // 首先获取用户偏好，成功后再初始化自动刷新服务
    preferencesStore.fetchPreferences().then(() => {
      initializeAutoRefresh();
    });
  } else {
    // 用户已登出
    // 停止自动刷新服务以清理定时器和监听器
    stopAutoRefresh();
  }
};

// 监听token的变化（例如，登录和登出操作）
watch(() => authStore.token, (newToken) => {
  handleAuthChange(newToken);
});

// 应用首次加载时，检查当前的登录状态
onMounted(() => {
  handleAuthChange(authStore.token);
});

// 在离开页面前确保DOM已准备好，避免insertBefore错误
function beforeLeave() {
  // 添加一个短暂延迟，确保DOM操作完成
  return new Promise(resolve => setTimeout(resolve, 50));
}

// 在进入页面前预处理
function beforeEnter() {
  // 添加一个短暂延迟，确保DOM操作完成
  return new Promise(resolve => setTimeout(resolve, 50));
}
</script>

<template>
  <RouterView v-slot="{ Component }">
    <transition name="fade" mode="out-in" @before-leave="beforeLeave" @before-enter="beforeEnter">
      <component :is="Component" :key="$route.fullPath" />
    </transition>
  </RouterView>
</template>

<style>
@import '@/assets/main.css';

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
  position: absolute;
  width: 100%;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 确保容器有足够高度，避免过渡时的跳动 */
#app {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden; /* 防止水平滚动条 */
}

/* 禁止在触摸设备上点击元素时出现蓝色高亮 */
* {
  -webkit-tap-highlight-color: transparent;
}

/* 添加全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.3);
  border-radius: 4px;
  transition: background 0.2s;
  }

::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.5);
  }

/* 输入框自动填充背景色调整 */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 30px rgba(255, 255, 255, 0.95) inset !important;
  transition: background-color 5000s ease-in-out 0s;
  }

/* 添加平滑滚动 */
html {
  scroll-behavior: smooth;
}
</style>
