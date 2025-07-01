<template>
  <MainLayout>
    <div class="feed-manage-container">
      <div class="feed-manage-header">
        <h1 class="page-title">订阅管理</h1>
        <button v-if="feeds.length > 0" @click="refreshFeeds" class="refresh-button" :disabled="isLoading">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="refresh-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
          刷新
        </button>
      </div>

      <!-- 订阅列表 -->
      <FeedList
        :feeds="groupedFeeds"
        :is-loading="isLoading"
        @add="openAddFeedDialog"
        @refresh="handleFeedRefresh"
        @delete="handleFeedDelete"
      />
    </div>

    <!-- 添加订阅对话框 -->
    <AddFeedDialog
      :is-open="isAddFeedDialogOpen"
      @close="isAddFeedDialogOpen = false"
      @added="handleFeedAdded"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import FeedList from '@/components/feed/FeedList.vue';
import AddFeedDialog from '@/components/feed/AddFeedDialog.vue';
import { useFeedStore } from '@/stores/feed';
import notification from '@/utils/notification';

const feedStore = useFeedStore();

// 状态
const isAddFeedDialogOpen = ref(false);

const feeds = computed(() => feedStore.feeds);
const isLoading = computed(() => feedStore.isLoading);

// 计算属性，将feeds按分类分组
const groupedFeeds = computed(() => {
  return feeds.value.reduce((acc, feed) => {
    const category = feed.category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(feed);
    return acc;
  }, {} as Record<string, typeof feeds.value>);
});

// 打开添加订阅对话框
const openAddFeedDialog = () => {
  isAddFeedDialogOpen.value = true;
};

// 处理订阅添加成功
const handleFeedAdded = () => {
  // 无需手动刷新，添加操作已在store中更新feeds数组
  notification.success('订阅添加成功！');
};

// 处理订阅刷新
const handleFeedRefresh = () => {
  // 无需额外操作，刷新操作已在store中更新feeds数组
};

// 处理订阅删除
const handleFeedDelete = () => {
  // 无需额外操作，删除操作已在store中更新feeds数组
};

// 手动刷新所有订阅
const refreshFeeds = () => {
  feedStore.fetchFeeds(true);
  notification.success('正在刷新订阅列表...');
};

// 页面加载时获取订阅列表，利用缓存机制
onMounted(() => {
  // 使用缓存，不强制刷新
  if (!feedStore.isCacheValid || feeds.value.length === 0) {
    feedStore.fetchFeeds();
  }
});
</script>

<style scoped>
.feed-manage-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.feed-manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-button:hover {
  background-color: #e5e7eb;
}

.refresh-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 640px) {
  .feed-manage-container {
    padding: 1rem;
  }

  .feed-manage-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
}
</style>
