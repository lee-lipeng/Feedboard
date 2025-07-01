<template>
  <div class="article-list">
    <!-- 加载状态 -->
    <div v-if="isLoading && articles.length === 0" class="article-list-loading">
      <div class="loading-spinner"></div>
      <p>加载文章中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!articles || articles.length === 0" class="article-list-empty">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
      </div>
      <p>{{ emptyMessage }}</p>
    </div>

    <!-- 文章列表 -->
    <div v-else class="articles-container">
      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card" 
        :class="{ 'article-read': article.is_read }"
        @click="$emit('view', article.id)"
      >
        <!-- 文章图片 -->
        <div class="article-image-container">
          <img 
            v-if="article.image_url" 
            :src="article.image_url" 
            :alt="article.title" 
            class="article-image" 
            @error="handleImageError"
          />
          <div v-else class="article-image-placeholder">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
            </svg>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="article-content">
          <h2 class="article-title">{{ article.title }}</h2>
          <p v-if="article.summary" class="article-summary">{{ formatSummary(article.summary) }}</p>
          
          <div class="article-meta">
            <span class="article-source">{{ article.feed_title }}</span>
            <span v-if="article.author" class="article-author">{{ article.author }}</span>
            <span v-if="article.published_at" class="article-date">{{ formatDate(article.published_at) }}</span>
          </div>
          
          <!-- 文章操作 -->
          <div class="article-actions">
            <button 
              class="action-button" 
              :class="{ 'active': article.is_favorite }"
              @click.stop="toggleFavorite(article)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
              </svg>
              <span>{{ article.is_favorite ? '已收藏' : '收藏' }}</span>
            </button>
            
            <button 
              class="action-button"
              :class="{ 'active': article.read_later }"
              @click.stop="toggleReadLater(article)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
              </svg>
              <span>{{ article.read_later ? '已加入稍后阅读' : '稍后阅读' }}</span>
            </button>
            
            <button 
              class="action-button"
              :class="{ 'disabled': article.is_read }"
              @click.stop="markAsRead(article)"
              :disabled="article.is_read"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{{ article.is_read ? '已读' : '标记为已读' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部加载状态 -->
    <div v-if="isLoading && articles.length > 0" class="bottom-loading">
      <div class="loading-spinner-small"></div>
      <p>努力加载中...</p>
    </div>
    
    <!-- 分页组件 -->
    <div v-if="!isLoading && articles.length > 0" class="pagination">
      <button 
        class="page-button"
        :disabled="pagination.page <= 1"
        @click="changePage(pagination.page - 1)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="page-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
        上一页
      </button>
      
      <div class="page-numbers">
        <!-- 第一页 -->
        <button 
          v-if="pagination.totalPages > 5 && pagination.page > 3" 
          class="page-number" 
          :class="{ active: pagination.page === 1 }"
          @click="changePage(1)"
        >
          1
        </button>
        
        <!-- 省略号 -->
        <span v-if="pagination.totalPages > 5 && pagination.page > 3" class="page-ellipsis">...</span>
        
        <!-- 页码 -->
        <button 
          v-for="pageNum in displayedPageNumbers" 
          :key="pageNum" 
          class="page-number" 
          :class="{ active: pagination.page === pageNum }"
          @click="changePage(pageNum)"
        >
          {{ pageNum }}
        </button>
        
        <!-- 省略号 -->
        <span v-if="pagination.totalPages > 5 && pagination.page < pagination.totalPages - 2" class="page-ellipsis">...</span>
        
        <!-- 最后一页 -->
        <button 
          v-if="pagination.totalPages > 5 && pagination.page < pagination.totalPages - 2" 
          class="page-number" 
          :class="{ active: pagination.page === pagination.totalPages }"
          @click="changePage(pagination.totalPages)"
        >
          {{ pagination.totalPages }}
        </button>
      </div>
      
      <button 
        class="page-button"
        :disabled="pagination.page >= pagination.totalPages"
        @click="changePage(pagination.page + 1)"
      >
        下一页
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="page-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      </button>
      
      <!-- 跳转到指定页 -->
      <div class="page-jump">
        <span>跳至</span>
        <input
          type="number"
          class="page-input"
          v-model="jumpToPage"
          min="1"
          :max="pagination.totalPages"
          @keyup.enter="handleJumpToPage"
        />
        <span>页</span>
        <button class="jump-button" @click="handleJumpToPage">跳转</button>
      </div>
      
      <div class="page-total">
        共 {{ pagination.total }} 条 / {{ pagination.totalPages }} 页
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useArticleStore, type Article } from '@/stores/article';
import notification from '@/utils/notification';

const props = defineProps({
  articles: {
    type: Array as () => Article[],
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  emptyMessage: {
    type: String,
    default: '暂无文章'
  },
  pagination: {
    type: Object as () => { total: number, page: number, totalPages: number },
    default: () => ({ total: 0, page: 1, totalPages: 1 })
  }
});

const emit = defineEmits(['view', 'update', 'change-page']);

const articleStore = useArticleStore();
const jumpToPage = ref<number | string>('');

// 计算显示的页码
const displayedPageNumbers = computed(() => {
  const totalPages = props.pagination.totalPages;
  const currentPage = props.pagination.page;
  
  if (totalPages <= 5) {
    // 总页数小于等于5，显示所有页码
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  } else {
    // 总页数大于5，显示当前页附近的页码
    let startPage = Math.max(currentPage - 2, 1);
    let endPage = Math.min(startPage + 4, totalPages);
    
    // 调整起始页，确保显示5个页码
    if (endPage - startPage < 4) {
      startPage = Math.max(endPage - 4, 1);
    }
    
    return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
  }
});

// 处理跳转页码
const handleJumpToPage = () => {
  if (!jumpToPage.value) return;
  
  const page = Number(jumpToPage.value);
  if (isNaN(page) || page < 1 || page > props.pagination.totalPages) {
    notification.error(`请输入1-${props.pagination.totalPages}之间的页码`);
    return;
  }
  
  changePage(page);
  jumpToPage.value = '';
};

// 切换页码
const changePage = (page: number) => {
  if (page < 1 || page > props.pagination.totalPages) return;
  emit('change-page', page);
};

// 标记为已读
async function markAsRead(article: Article) {
  if (article.is_read) return;
  
  try {
    const result = await articleStore.updateArticleStatus(article.id, { is_read: true });
    if (result) {
      emit('update', article.id);
    }
  } catch (error) {
    console.error('标记已读失败:', error);
    notification.error('操作失败，请稍后重试');
  }
}

// 切换收藏状态
async function toggleFavorite(article: Article) {
  try {
    const result = await articleStore.updateArticleStatus(article.id, { 
      is_favorite: !article.is_favorite 
    });
    if (result) {
      emit('update', article.id);
      
      if (!article.is_favorite) {
        notification.success('已添加到收藏');
      } else {
        notification.success('已取消收藏');
      }
      
      // 触发自定义事件,通知更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } catch (error) {
    console.error('更新收藏状态失败:', error);
    notification.error('操作失败，请稍后重试');
  }
}

// 切换稍后阅读状态
async function toggleReadLater(article: Article) {
  try {
    const result = await articleStore.updateArticleStatus(article.id, { 
      read_later: !article.read_later 
    });
    if (result) {
      emit('update', article.id);
      
      if (!article.read_later) {
        notification.success('已添加到稍后阅读');
      } else {
        notification.success('已从稍后阅读中移除');
      }
      
      // 触发自定义事件,通知更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } catch (error) {
    console.error('更新稍后阅读状态失败:', error);
    notification.error('操作失败，请稍后重试');
  }
}

// 格式化摘要，限制长度
function formatSummary(summary: string): string {
  if (!summary) return '';
  
  // 移除HTML标签
  const plainText = summary.replace(/<[^>]+>/g, '');
  
  // 限制长度
  const maxLength = 150;
  if (plainText.length <= maxLength) return plainText;
  
  return plainText.substring(0, maxLength) + '...';
}

// 格式化日期
function formatDate(dateString: string | null): string {
  if (!dateString) return '';
  
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
}

// 处理图片加载错误
function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
  const container = target.parentElement;
  if (container) {
    const placeholder = document.createElement('div');
    placeholder.className = 'article-image-placeholder';
    placeholder.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
      </svg>
    `;
    container.appendChild(placeholder);
  }
}
</script>

<style scoped>
.article-list {
  width: 100%;
}

/* 加载状态 */
.article-list-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-spinner-small {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部加载状态 */
.bottom-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 0;
  color: #6b7280;
  font-size: 0.875rem;
}

/* 分页组件 */
.pagination {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 2rem;
  padding: 1rem 0;
  gap: 0.75rem;
}

.page-button {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.page-button:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #1f2937;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-icon {
  width: 1rem;
  height: 1rem;
  margin: 0 0.25rem;
}

.page-numbers {
  display: flex;
  align-items: center;
}

.page-number {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #e5e7eb;
  margin: 0 0.25rem;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.page-number:hover:not(.active) {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #1f2937;
}

.page-number.active {
  background-color: #6366f1;
  border-color: #6366f1;
  color: white;
  font-weight: 600;
}

.page-ellipsis {
  margin: 0 0.25rem;
  color: #6b7280;
}

.page-jump {
  display: flex;
  align-items: center;
  margin-left: 0.75rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.page-input {
  width: 3rem;
  height: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 0 0.5rem;
  margin: 0 0.5rem;
  text-align: center;
  font-size: 0.875rem;
}

.jump-button {
  padding: 0.375rem 0.75rem;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.jump-button:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #1f2937;
}

.page-total {
  margin-left: 0.75rem;
  font-size: 0.875rem;
  color: #6b7280;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
  
  .page-jump {
    margin-left: 0;
  }
  
  .page-total {
    margin-left: 0;
  }
}

/* 空状态 */
.article-list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  text-align: center;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.article-list-empty p {
  color: #4b5563;
}

/* 文章列表 */
.articles-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

/* 文章卡片 */
.article-card {
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
}

.article-read {
  opacity: 0.7;
}

/* 文章图片 */
.article-image-container {
  width: 100%;
  height: 180px;
  overflow: hidden;
  position: relative;
  background-color: #f3f4f6;
}

.article-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.article-card:hover .article-image {
  transform: scale(1.05);
}

.article-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #9ca3af;
}

.article-image-placeholder svg {
  width: 3rem;
  height: 3rem;
}

/* 文章内容 */
.article-content {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.article-summary {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1rem;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* 文章元数据 */
.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.75rem;
  gap: 0.5rem;
}

.article-source {
  color: #6366f1;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  background-color: #ede9fe;
  border-radius: 0.25rem;
}

.article-author {
  color: #4b5563;
}

.article-date {
  color: #6b7280;
}

/* 文章操作 */
.article-actions {
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid #f3f4f6;
  padding-top: 1rem;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
}

.article-actions::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.75rem;
  background-color: #f9fafb;
  border: none;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-button:hover:not(.disabled) {
  background-color: #f3f4f6;
  color: #1f2937;
}

.action-button.active {
  background-color: #ede9fe;
  color: #6366f1;
}

.action-button.disabled {
  opacity: 0.5;
  cursor: default;
}

.action-icon {
  width: 1rem;
  height: 1rem;
  margin-right: 0.25rem;
  flex-shrink: 0;
}

/* 响应式布局 */
@media (min-width: 640px) {
  .article-card {
    flex-direction: row;
  }
  
  .article-image-container {
    width: 200px;
    height: auto;
    flex-shrink: 0;
  }
}

@media (min-width: 768px) {
  .articles-container {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .article-card {
    flex-direction: column;
  }
  
  .article-image-container {
    width: 100%;
    height: 180px;
  }
}

@media (min-width: 1280px) {
  .articles-container {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}
</style> 