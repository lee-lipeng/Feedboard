<template>
  <div class="main-layout" :style="{ '--sidebar-width': sidebarWidth + 'px' }">
    <!-- 顶部导航栏 -->
    <header class="main-header">
      <div class="header-container">
        <!-- Logo 和站点名称 -->
        <div class="header-logo">
          <router-link to="/" class="logo-link">
            <img src="@/assets/logo.svg" alt="Feedboard Logo" class="logo-img" />
            <span class="logo-text">Feedboard</span>
          </router-link>
        </div>
        
        <!-- 搜索框 -->
        <div class="search-container">
          <input 
            type="text" 
            placeholder="搜索文章..." 
            class="search-input"
            @focus="isSearchFocused = true"
            @blur="isSearchFocused = false"
            v-model="searchQuery"
            @keydown.enter="handleSearch"
          />
          <button class="search-button" @click="handleSearch">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="search-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
          </button>
        </div>
        
        <!-- 用户菜单 -->
        <div class="user-menu">
          <div class="user-avatar" @click="toggleUserDropdown">
            <span class="avatar-text">{{ userInitials }}</span>
          </div>
          
          <!-- 用户下拉菜单 -->
          <div v-if="isUserDropdownOpen" class="user-dropdown">
            <div class="dropdown-user-info">
              <span class="dropdown-username">{{ userEmail }}</span>
            </div>
            <div class="dropdown-divider"></div>
            <ul class="dropdown-menu">
              <li>
                <router-link to="/profile" class="dropdown-item">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="dropdown-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  个人中心
                </router-link>
              </li>
              <li>
                <router-link to="/settings" class="dropdown-item">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="dropdown-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  设置
                </router-link>
              </li>
              <li>
                <button @click="logout" class="dropdown-item">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="dropdown-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                  </svg>
                  退出登录
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <!-- 添加订阅按钮 - 移至顶部 -->
        <div class="add-subscription">
          <button class="add-button" @click="openAddFeedDialog">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="add-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            添加订阅
          </button>
        </div>
        
        <div class="sidebar-content">
          <!-- 浏览分组 -->
          <div class="subscription-group">
            <div class="group-header">
              <h3 class="group-title">浏览</h3>
            </div>
            <ul class="subscription-list">
              <li class="subscription-item" :class="{ active: currentRouteName === 'home' }">
                <router-link to="/" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" />
                  </svg>
                  全部文章
                </router-link>
              </li>
              <li class="subscription-item" :class="{ active: currentRouteName === 'latest' }">
                <router-link to="/latest" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  最新更新
                </router-link>
              </li>
              <li class="subscription-item" :class="{ active: currentRouteName === 'unread' }">
                <router-link to="/unread" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 00-1.883 2.542l.857 6a2.25 2.25 0 002.227 1.932H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-1.883-2.542m-16.5 0V6A2.25 2.25 0 016 3.75h3.879a1.5 1.5 0 011.06.44l2.122 2.12a1.5 1.5 0 001.06.44H18A2.25 2.25 0 0120.25 9v.776" />
                  </svg>
                  未读文章
                </router-link>
              </li>
            </ul>
          </div>

          <!-- 个人收藏分组 -->
          <div class="subscription-group">
            <div class="group-header">
              <h3 class="group-title">个人收藏</h3>
            </div>
            <ul class="subscription-list">
              <li class="subscription-item" :class="{ active: currentRouteName === 'favorites' }">
                <router-link to="/favorites" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                  </svg>
                  我的收藏
                  <span v-if="favoriteCount > 0" class="item-badge">{{ favoriteCount }}</span>
                </router-link>
              </li>
              <li class="subscription-item" :class="{ active: currentRouteName === 'read-later' }">
                <router-link to="/read-later" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
                  </svg>
                  稍后阅读
                  <span v-if="readLaterCount > 0" class="item-badge">{{ readLaterCount }}</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- 订阅管理分组 -->
          <div class="subscription-group">
            <div class="group-header">
              <h3 class="group-title">订阅管理</h3>
            </div>
            <ul class="subscription-list">
              <li class="subscription-item" :class="{ active: currentRouteName === 'feeds' }">
                <router-link to="/feeds" class="subscription-link" @click="closeSidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12.75 19.5v-.75a7.5 7.5 0 00-7.5-7.5H4.5m0-6.75h.75c7.87 0 14.25 6.38 14.25 14.25v.75M6 18.75L18 6.75" />
              </svg>
                  全部订阅
                </router-link>
              </li>
            </ul>
          </div>

          <!-- 我的订阅 -->
          <div class="subscription-group">
            <div class="group-header">
              <h3 class="group-title">我的订阅</h3>
            </div>
            <ul v-if="feeds.length > 0" class="subscription-list">
              <li
                v-for="feed in feeds"
                :key="feed.feed_id"
                class="subscription-item"
                :class="{ active: currentRouteName === 'feed-detail' && Number(route.params.feedId) === feed.feed_id }"
              >
                <router-link :to="`/feeds/${feed.feed_id}`" class="subscription-link" @click="handleFeedClick(feed.feed_id)">
                  <img v-if="feed.feed_image_url" :src="feed.feed_image_url" class="item-icon feed-favicon" alt=""/>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="item-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12.75 19.5v-.75a7.5 7.5 0 00-7.5-7.5H4.5m0-6.75h.75c7.87 0 14.25 6.38 14.25 14.25v.75M6 18.75L18 6.75" />
              </svg>
                  <span class="subscription-title">{{ feed.title_override || feed.feed_title }}</span>
                  <span v-if="getUnreadCount(feed.feed_id) > 0" class="unread-badge">
                    {{ getUnreadCount(feed.feed_id) }}
                  </span>
                </router-link>
              </li>
            </ul>
            <div v-else class="no-feeds-message">
              暂无订阅
            </div>
          </div>
        </div>
      </aside>

      <!-- 侧边栏切换按钮 - 移到侧边栏外部 -->
      <button class="sidebar-toggle-button" @click="toggleSidebar">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="toggle-icon">
          <path v-if="isSidebarCollapsed" stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>
      
      <!-- 页面内容 -->
      <main class="page-content" :class="{ 'content-expanded': isSidebarCollapsed }">
        <slot></slot>
      </main>
    </div>

    <!-- 添加订阅对话框 -->
    <AddFeedDialog 
      :is-open="isAddFeedDialogOpen"
      @close="isAddFeedDialogOpen = false"
      @added="handleFeedAddedNew"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { usePreferencesStore } from '@/stores/preferences';
import { useRouter, useRoute } from 'vue-router';
import { useArticleStore } from '@/stores/article';
import { useFeedStore } from '@/stores/feed';
import { useUnreadStore } from '@/stores/unread';
import AddFeedDialog from '@/components/feed/AddFeedDialog.vue';
import notification from '@/utils/notification';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();
const feedStore = useFeedStore();
const articleStore = useArticleStore();
const router = useRouter();
const route = useRoute();
const { unreadCount, favoriteCount, readLaterCount } = storeToRefs(articleStore);
const { feeds, isLoading: feedsLoading, error: feedsError } = storeToRefs(feedStore);

const unreadStore = useUnreadStore();
const { getUnreadCount } = unreadStore;

// 侧边栏宽度 - 用于动态计算按钮位置
const sidebarWidth = ref(235);

// 获取当前路由路径
const currentRoute = computed(() => route.path);

// 当前路由名称
const currentRouteName = computed(() => route.name);

// 获取订阅源徽章计数
const updateBadgeCounts = async () => {
  await articleStore.fetchBadgeCounts();
};

// 组件挂载时获取一次
onMounted(() => {
  // 如果用户已认证，则获取其订阅列表以填充侧边栏
  if (authStore.isAuthenticated) {
    feedStore.fetchFeeds();
  }

  updateBadgeCounts();

  // 监听自定义事件,用于更新徽章计数
  document.addEventListener('update-badge-counts', updateBadgeCounts);
});

// 组件卸载时移除事件监听器
onUnmounted(() => {
  document.removeEventListener('update-badge-counts', updateBadgeCounts);
});

// 添加订阅对话框
const isAddFeedDialogOpen = ref(false);

// 打开添加订阅对话框
const openAddFeedDialog = () => {
  isAddFeedDialogOpen.value = true;
};

// 处理订阅添加成功
const handleFeedAddedNew = () => {
  isAddFeedDialogOpen.value = false;
  // 后台任务开始的即时反馈
  notification.info('已提交订阅请求，正在后台处理...');
  
  // 短暂延迟后刷新订阅列表，此时新订阅应该已经可见（但可能无标题）
  setTimeout(() => {
    feedStore.fetchFeeds(true); // 强制刷新订阅列表
  }, 500);

  // WebSocket会处理后续的完成通知和文章缓存失效，所以这里无需调用articleStore
};

// 用户下拉菜单
const isUserDropdownOpen = ref(false);
const toggleUserDropdown = () => {
  isUserDropdownOpen.value = !isUserDropdownOpen.value;
};

// 点击外部关闭下拉菜单
document.addEventListener('click', (event) => {
  if (isUserDropdownOpen.value && !(event.target as Element).closest('.user-menu')) {
    isUserDropdownOpen.value = false;
  }
});

// 用户信息
const userEmail = computed(() => authStore.user?.email || '');
const userInitials = computed(() => {
  if (!authStore.user?.email) return '?';
  return authStore.user.email.charAt(0).toUpperCase();
});

// 搜索
const searchQuery = ref('');
const isSearchFocused = ref(false);

// 侧边栏收起/展开
const isSidebarCollapsed = ref(window.innerWidth < 1024);

// 显示或隐藏侧边栏
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

// 关闭侧边栏
const closeSidebar = () => {
  if (window.innerWidth < 768) {
    isSidebarCollapsed.value = true;
  }
};

// 登出
const logout = () => {
  authStore.logout();
};

const handleFeedClick = (feedId: number) => {
  unreadStore.resetUnreadCount(feedId);
  closeSidebar();
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value } })
  }
}
</script>

<style scoped>
/* 全局变量定义 */
:root {
  --sidebar-width: 235px; /* 侧边栏宽度默认值235，会被sidebarWidth动态覆盖 */
}

/* 主布局 */
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 顶部导航栏 */
.main-header {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 0 1.5rem;
  height: 60px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}

.header-container {
  max-width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo 区域 */
.header-logo {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #1f2937;
}

.logo-img {
  width: 32px;
  height: 32px;
  margin-right: 0.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  display: none;
}

/* 搜索框 */
.search-container {
  position: relative;
  flex: 1;
  max-width: 500px;
  margin: 0 1rem;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 9999px;
  background-color: rgba(249, 250, 251, 0.8);
  font-size: 0.875rem;
  color: #1f2937;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #6366f1;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-button {
  position: absolute;
  left: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.search-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 用户菜单 */
.user-menu {
  position: relative;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar:hover {
  background-color: #4f46e5;
}

.avatar-text {
  font-size: 0.875rem;
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 240px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
  animation: dropdownFadeIn 0.2s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-user-info {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.dropdown-username {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  word-break: break-all;
}

.dropdown-divider {
  height: 1px;
  background-color: #f3f4f6;
}

.dropdown-menu {
  list-style: none;
  padding: 0.5rem 0;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.625rem 1rem;
  color: #4b5563;
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background-color: rgba(249, 250, 251, 0.8);
  color: #1f2937;
}

.dropdown-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.75rem;
  color: #6b7280;
}

/* 主内容区 */
.main-content {
  display: flex;
  margin-top: 60px;
  flex: 1;
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width, 235px);
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-right: 1px solid #e5e7eb;
  height: calc(100vh - 60px);
  position: fixed;
  left: 0;
  top: 60px;
  overflow-y: auto;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 40;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.sidebar::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.sidebar-collapsed {
  transform: translateX(calc(-1 * var(--sidebar-width)));
}

.sidebar-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 0 0.5rem;
}

/* 添加订阅按钮 - 移至顶部 */
.add-subscription {
  padding: 0 1.75rem 1rem;
  margin-bottom: 0.5rem;
}

.add-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.75rem 0.875rem;
  background-color: #f3f4f6;
  border: none;
  border-radius: 0.5rem;
  color: #4b5563;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-button:hover {
  background-color: #e5e7eb;
  color: #1f2937;
}

.add-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

/* 侧边栏切换按钮 */
.sidebar-toggle-button {
  position: fixed;
  left: calc(var(--sidebar-width) - 14px); /* 动态计算位置，略微偏左 */
  top: 50%; /* 垂直居中 */
  transform: translateY(-50%); /* 垂直居中调整 */
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100; /* 确保按钮在最上层 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-collapsed + .sidebar-toggle-button {
  left: 14px; /* 当侧边栏收起时，按钮移动到左侧边缘 */
}

.sidebar-toggle-button:hover {
  background-color: #f9fafb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.toggle-icon {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
}

/* 页面内容 */
.page-content {
  flex-grow: 1;
  padding: 1.5rem;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.3s ease;
  overflow-y: auto; /* 允许垂直滚动 */
  height: calc(100vh - 64px); /* 确保有一个确定的高度 */
}

.content-expanded {
  margin-left: 0;
}

/* 订阅分组相关样式 */
.subscription-group {
  margin-bottom: 1.5rem;
}

.group-header {
  padding: 0 1.25rem;
  margin-bottom: 0.5rem;
}

.group-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.subscription-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.subscription-item {
  display: block;
  margin-bottom: 0.125rem;
}

.subscription-link {
  display: flex;
  align-items: center;
  padding: 0.625rem 1.25rem;
  padding-left: 1.75rem;
  color: #4b5563;
  text-decoration: none;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  position: relative;
  font-size: 0.9375rem;
}

.subscription-link:hover {
  background-color: rgba(243, 244, 246, 0.8);
  color: #1f2937;
}

.subscription-item.active .subscription-link {
  background-color: rgba(239, 246, 255, 0.8);
  color: #3b82f6;
  font-weight: 500;
}

.item-icon {
  width: 1.375rem;
  height: 1.375rem;
  margin-right: 0.75rem;
}

.item-badge {
  position: absolute;
  right: 12px;
  background-color: #6366f1;
  color: white;
  border-radius: 9999px;
  font-size: 0.75rem;
  min-width: 1.5rem;
  height: 1.5rem;
  padding: 0 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 1023px) {
  .page-content {
    margin-left: 0;
  }
  
  .sidebar {
    transform: translateX(calc(-1 * var(--sidebar-width)));
  }
  
  .sidebar-toggle-button {
    left: 1px;
  }

  .sidebar:not(.sidebar-collapsed) + .sidebar-toggle-button {
    left: calc(var(--sidebar-width) - 10px);
  }
}

@media (min-width: 768px) {
  .logo-text {
    display: block;
  }
  
  .search-container {
    margin: 0 2rem;
  }
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  color: #4b5563;
  text-decoration: none;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:hover {
  background-color: rgba(243, 244, 246, 0.8);
  color: #1f2937;
}

.menu-item.active {
  background-color: rgba(239, 246, 255, 0.8);
  color: #3b82f6;
  font-weight: 500;
}

.menu-icon {
  width: 1.375rem;
  height: 1.375rem;
  margin-right: 0.75rem;
}

.menu-text {
  font-size: 0.9375rem;
}

.menu-badge {
  position: absolute;
  right: 12px;
  background-color: #6366f1;
  color: white;
  border-radius: 9999px;
  font-size: 0.75rem;
  min-width: 1.5rem;
  height: 1.5rem;
  padding: 0 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.subscription-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
  margin-right: 8px; /* 与角标保持距离 */
}

.feed-favicon {
  border-radius: 4px;
  object-fit: cover;
}

.no-feeds-message {
  padding: 0.625rem 1.75rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.unread-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  font-size: 12px;
  font-weight: 500;
  margin-left: auto;
  flex-shrink: 0;
}
</style> 
