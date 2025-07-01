<template>
  <MainLayout>
    <div class="favorites-container">
      <div class="page-header">
        <h1 class="page-title">我的收藏</h1>

        <div class="header-actions" v-if="articles.length > 0">
              <button 
            class="action-btn"
            @click="markAllAsRead"
            :disabled="isLoading"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
            全部标为已读
              </button>
              
              <button 
            class="action-btn"
            @click="refreshArticles"
            :disabled="isLoading"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
            刷新
              </button>
        </div>
      </div>
      
      <!-- 加载状态显示 -->
      <div v-if="isLoading && !initialDataLoaded" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在加载收藏文章...</p>
      </div>

      <!-- 文章列表/详情视图 -->
      <template v-else>
        <Transition name="article-list" mode="out-in" appear>
          <template v-if="currentView === 'list'">
            <ArticleList
              :articles="articles"
              :is-loading="isLoading && initialDataLoaded"
              :empty-message="'您没有收藏任何文章'"
              :pagination="pagination"
              @view="viewArticle"
              @update="handleArticleUpdate"
              @change-page="changePage"
            />
          </template>
        </Transition>

        <Transition name="article-detail" mode="out-in" appear>
          <template v-if="currentView === 'detail'">
            <ArticleDetail
              :article-id="currentArticleId!"
              :article="currentArticle"
              :is-loading="isLoading && initialDataLoaded"
              @update="handleArticleUpdate"
              @back="backToList"
            />
          </template>
        </Transition>
      </template>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import ArticleList from '@/components/article/ArticleList.vue';
import ArticleDetail from '@/components/article/ArticleDetail.vue';
import { useArticleStore } from '@/stores/article';
import notification from '@/utils/notification';

const articleStore = useArticleStore();

// 页面状态
const currentView = ref<'list' | 'detail'>('list');
const currentArticleId = ref<number | null>(null);
const pageSize = ref(10);
const currentPage = ref(1);
const initialDataLoaded = ref(false); // 标记初始数据是否已加载

// 分页信息
const pagination = ref({
  total: 0,
  page: 1,
  totalPages: 1
});

// 计算属性
const articles = computed(() => articleStore.articles);
const isLoading = computed(() => articleStore.isLoading);
const currentArticle = computed(() =>
  currentArticleId.value
    ? articleStore.getArticleById(currentArticleId.value)
    : null
);

// 获取收藏文章
const fetchFavoriteArticles = async (page = 1) => {
  try {
    const skip = (page - 1) * pageSize.value;
    const result = await articleStore.fetchArticles({
      skip,
      limit: pageSize.value,
      is_favorite: true
    }, true);

    // 处理分页响应
    if (result && 'data' in result) {
      // 更新分页信息
      pagination.value = {
        total: result.total || 0,
        page: page,
        totalPages: result.totalPages || Math.ceil((result.total || 0) / pageSize.value)
      };

      currentPage.value = page;
    }
    
    // 标记初始数据已加载
    initialDataLoaded.value = true;
    return result;
  } catch (error) {
    console.error('获取收藏文章失败:', error);
    notification.error('获取文章失败，请稍后重试');
    initialDataLoaded.value = true; // 即使出错也标记为已加载
    return [];
  }
};

// 切换页码
const changePage = async (page: number) => {
  if (page < 1 || page > pagination.value.totalPages) return;

  window.scrollTo({ top: 0, behavior: 'smooth' });
  await fetchFavoriteArticles(page);
};

// 查看文章详情
const viewArticle = async (articleId: number) => {
  currentArticleId.value = articleId;
  currentView.value = 'detail';

  // 如果本地没有文章详情，从服务器获取
  if (!currentArticle.value) {
    await articleStore.fetchArticle(articleId);
  }
};

// 返回文章列表
const backToList = () => {
  currentView.value = 'list';
  currentArticleId.value = null;
  
  // 返回列表时刷新数据,确保列表是最新的
  fetchFavoriteArticles(currentPage.value);
};

// 处理文章更新
const handleArticleUpdate = async (articleId?: number) => {
  // 检查是否为取消收藏操作
  if (articleId && currentView.value === 'detail') {
    // 获取文章
    const article = articleStore.getArticleById(articleId);
    
    // 如果文章存在且不再是收藏状态,不自动返回列表,只更新本地数据
    if (article && !article.is_favorite) {
      // 不再自动跳转到列表页
      // 只在本地更新数据,当用户手动返回时列表会刷新
      
      // 触发自定义事件,通知父组件更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } else {
    // 重新获取当前页的数据
    await fetchFavoriteArticles(currentPage.value);
    
    // 触发自定义事件,通知父组件更新徽章计数
    document.dispatchEvent(new CustomEvent('update-badge-counts'));
  }
};

// 刷新文章
const refreshArticles = () => {
  initialDataLoaded.value = false; // 重置加载状态
  fetchFavoriteArticles(1);
};

// 标记所有为已读
const markAllAsRead = async () => {
  try {
    await articleStore.markAllAsRead();
    notification.success('已将所有文章标记为已读');
    refreshArticles();
  } catch (error) {
    console.error('标记已读失败:', error);
    notification.error('操作失败，请稍后重试');
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  await fetchFavoriteArticles(1);
});
</script>

<style scoped>
.favorites-container {
  max-width: 100%;
  padding: 1rem;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 180px);
  padding: 2rem;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid rgba(99, 102, 241, 0.1);
  border-left-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-text {
  color: #6b7280;
  font-size: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 添加页面过渡效果 */
.article-list-enter-active,
.article-list-leave-active,
.article-detail-enter-active,
.article-detail-leave-active {
  transition: opacity 0.15s ease;
}

.article-list-enter-from,
.article-list-leave-to,
.article-detail-enter-from,
.article-detail-leave-to {
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background-color: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: #e5e7eb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-icon {
  width: 1rem;
  height: 1rem;
}

/* 响应式调整 */
@media (min-width: 640px) {
  .favorites-container {
    padding: 1.5rem;
  }
}

@media (min-width: 768px) {
  .page-title {
    font-size: 1.75rem;
  }
}

@media (min-width: 1024px) {
  .page-title {
    font-size: 2rem;
  }
}
</style>
