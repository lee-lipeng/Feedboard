<template>
  <div class="feed-list">
    <div class="feed-list-header">
      <h2 class="feed-list-title">我的订阅</h2>
      <button class="add-feed-button" @click="$emit('add')">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="add-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        添加订阅
      </button>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="feed-list-loading">
      <div class="loading-spinner"></div>
      <p>加载订阅中...</p>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="Object.keys(feeds).length === 0" class="feed-list-empty">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12.75 19.5v-.75a7.5 7.5 0 00-7.5-7.5H4.5m0-6.75h.75c7.87 0 14.25 6.38 14.25 14.25v.75M6 18.75L18 6.75" />
        </svg>
      </div>
      <p>暂无订阅源</p>
      <button class="add-feed-button-empty" @click="$emit('add')">添加第一个订阅</button>
    </div>
    
    <!-- 订阅列表 -->
    <div v-else class="feed-list-content">
      <div v-for="(feedItems, category) in feeds" :key="category" class="feed-category-group">
        <h3 class="category-title" @click="toggleCategory(category)">
          <span>{{ getCategoryLabel(category as FeedCategory) }}</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="category-toggle-icon"
            :class="{ 'is-collapsed': collapsedCategories.has(category) }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </h3>
        <div v-if="!collapsedCategories.has(category)" class="feed-items-container">
          <div v-for="feed in feedItems" :key="feed.id" class="feed-item">
            <div class="feed-item-content">
              <div class="feed-icon">
                <img v-if="feed.feed_image_url" :src="feed.feed_image_url" :alt="feed.feed_title" class="feed-icon-img">
                <div v-else class="feed-icon-placeholder">
                  {{ feed.feed_title.charAt(0).toUpperCase() }}
                </div>
              </div>
              <div class="feed-details">
                <h3 class="feed-title">{{ feed.title_override || feed.feed_title }}</h3>
                <p v-if="feed.feed_description" class="feed-description">{{ feed.feed_description }}</p>
                <div class="feed-meta">
                  <span class="feed-category">{{ getCategoryLabel(feed.category) }}</span>
                  <span v-if="feed.feed_last_fetched" class="feed-last-updated">
                    更新于: {{ formatDate(feed.feed_last_fetched) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="feed-actions">
              <button class="feed-action-button refresh-button" @click="refreshFeed(feed.feed_id)" :disabled="isRefreshing">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
              </button>
              <button class="feed-action-button delete-button" @click="confirmDeleteFeed(feed)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="delete-confirm-overlay" @click="cancelDelete">
      <div class="delete-confirm-dialog" @click.stop>
        <h3 class="delete-confirm-title">删除订阅</h3>
        <p class="delete-confirm-message">
          确定要删除订阅 <strong>{{ feedToDelete?.title_override || feedToDelete?.feed_title }}</strong> 吗？该操作无法撤销。
        </p>
        <div class="delete-confirm-actions">
          <button class="cancel-button" @click="cancelDelete">取消</button>
          <button class="delete-confirm-button" @click="deleteFeed()" :disabled="isDeleting">
            <span v-if="isDeleting" class="loading-spinner-sm"></span>
            {{ isDeleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useFeedStore, FeedCategory } from '@/stores/feed';
import type { Feed } from '@/stores/feed';
import notification from '@/utils/notification';

const props = defineProps({
  feeds: {
    type: Object as () => Record<string, Feed[]>,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['add', 'refresh', 'delete']);

const feedStore = useFeedStore();

// 记录折叠的分类
const collapsedCategories = ref(new Set<string>());

// 切换分类折叠状态
const toggleCategory = (category: string) => {
  if (collapsedCategories.value.has(category)) {
    collapsedCategories.value.delete(category);
  } else {
    collapsedCategories.value.add(category);
  }
};

// 刷新状态
const isRefreshing = ref(false);

// 删除相关状态
const showDeleteConfirm = ref(false);
const feedToDelete = ref<Feed | null>(null);
const isDeleting = ref(false);

// 显示分类标签
const getCategoryLabel = (category: string) => {
  const categoryMap: Record<string, string> = {
    [FeedCategory.NEWS]: '新闻',
    [FeedCategory.TECH]: '技术',
    [FeedCategory.DESIGN]: '设计',
    [FeedCategory.BUSINESS]: '商业',
    [FeedCategory.ENTERTAINMENT]: '娱乐',
    [FeedCategory.SPORTS]: '体育',
    [FeedCategory.SCIENCE]: '科学',
    [FeedCategory.HEALTH]: '健康',
    [FeedCategory.BLOG]: '博客',
    [FeedCategory.OTHER]: '其他'
  };
  
  return categoryMap[category] || '其他';
};

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  
  // 今天的日期，显示时间
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  }
  
  // 昨天的日期
  const yesterday = new Date();
  yesterday.setDate(now.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  }
  
  // 一周内的日期
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays < 7) {
    return `${weekDays[date.getDay()]} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  }
  
  // 其他日期
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

// 刷新订阅
const refreshFeed = async (feedId: number) => {
  isRefreshing.value = true;
  
  try {
    const result = await feedStore.refreshFeed(feedId);
    if (result) {
      notification.success('订阅刷新成功！');
      emit('refresh', result);
    } else {
      notification.error(feedStore.error || '刷新失败，请稍后重试');
    }
  } catch (error) {
    console.error('刷新订阅失败:', error);
    notification.error('刷新失败，请稍后重试');
  } finally {
    isRefreshing.value = false;
  }
};

// 显示删除确认对话框
const confirmDeleteFeed = (feed: Feed) => {
  feedToDelete.value = feed;
  showDeleteConfirm.value = true;
};

// 取消删除
const cancelDelete = () => {
  showDeleteConfirm.value = false;
  feedToDelete.value = null;
};

// 执行删除
const deleteFeed = async () => {
  if (!feedToDelete.value) return;
  
  isDeleting.value = true;
  
  try {
    const result = await feedStore.deleteFeed(feedToDelete.value.feed_id);
    if (result) {
      notification.success(`订阅 ${feedToDelete.value.title_override || feedToDelete.value.feed_title} 已删除`);
      emit('delete', feedToDelete.value.feed_id);
      showDeleteConfirm.value = false;
      feedToDelete.value = null;
    } else {
      notification.error(feedStore.error || '删除失败，请稍后重试');
    }
  } catch (error) {
    console.error('删除订阅失败:', error);
    notification.error('删除失败，请稍后重试');
  } finally {
    isDeleting.value = false;
  }
};
</script>

<style scoped>
.feed-list {
  width: 100%;
  position: relative;
}

.feed-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.feed-list-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.add-feed-button {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-feed-button:hover {
  background-color: #4f46e5;
}

.add-icon {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}

/* 加载状态 */
.feed-list-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  color: #6b7280;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #e5e7eb;
  border-radius: 50%;
  border-top-color: #6366f1;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-spinner-sm {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 空状态 */
.feed-list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  color: #6b7280;
  text-align: center;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.add-feed-button-empty {
  margin-top: 1.5rem;
  padding: 0.625rem 1.25rem;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-feed-button-empty:hover {
  background-color: #4f46e5;
}

/* 订阅列表 */
.feed-list-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feed-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.feed-item:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.feed-item-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.feed-icon {
  width: 3rem;
  height: 3rem;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 0.375rem;
}

.feed-icon-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.feed-icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #6366f1;
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
}

.feed-details {
  flex: 1;
  min-width: 0;
}

.feed-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.feed-description {
  font-size: 0.875rem;
  color: #4b5563;
  margin: 0 0 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
}

.feed-category {
  padding: 0.125rem 0.5rem;
  background-color: #f3f4f6;
  color: #4b5563;
  border-radius: 9999px;
}

.feed-last-updated {
  color: #6b7280;
}

.feed-actions {
  display: flex;
  gap: 0.5rem;
}

.feed-action-button {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.375rem;
  background-color: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.feed-action-button:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.feed-action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-button:hover {
  color: #6366f1;
}

.delete-button:hover {
  color: #ef4444;
}

.action-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* 删除确认对话框 */
.delete-confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.delete-confirm-dialog {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.delete-confirm-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem;
}

.delete-confirm-message {
  font-size: 0.875rem;
  color: #4b5563;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.delete-confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-button {
  padding: 0.625rem 1rem;
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background-color: #e5e7eb;
  color: #1f2937;
}

.delete-confirm-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-confirm-button:hover:not(:disabled) {
  background-color: #dc2626;
}

.delete-confirm-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .feed-icon {
    width: 2.5rem;
    height: 2.5rem;
  }
  
  .feed-description {
    display: none;
  }
  
  .feed-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

.feed-category-group {
  margin-bottom: auto;
}

.category-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none; /* 防止选中文本 */
}

.category-toggle-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.2s ease-in-out;
}

.category-toggle-icon.is-collapsed {
  transform: rotate(-90deg);
}

.feed-items-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style> 