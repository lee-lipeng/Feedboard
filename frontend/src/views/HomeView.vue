<script setup lang="ts">
import { ref, onMounted, computed, watch, onBeforeMount } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import ArticleList from '@/components/article/ArticleList.vue';
import ArticleDetail from '@/components/article/ArticleDetail.vue';
import { useAuthStore } from '@/stores/auth';
import { useFeedStore } from '@/stores/feed';
import { useArticleStore } from '@/stores/article';
import notification from '@/utils/notification';

const authStore = useAuthStore();
const feedStore = useFeedStore();
const articleStore = useArticleStore();

// 页面状态
const currentView = ref<'list' | 'detail'>('list');
const currentArticleId = ref<number | null>(null);
const isLoading = ref(false);
const pageSize = ref(10);
const currentPage = ref(1);

// 分页信息
const pagination = ref({
  total: 0,
  page: 1,
  totalPages: 1
});

// 计算属性
const articles = computed(() => articleStore.articles);
const isArticleLoading = computed(() => articleStore.isLoading);
const currentArticle = computed(() =>
  currentArticleId.value
    ? articleStore.getArticleById(currentArticleId.value)
    : null
);
const feeds = computed(() => feedStore.feeds);

// 在script部分添加:
const initialDataLoaded = ref(false); // 标记初始数据是否已加载

// 在组件挂载前重置文章列表
onBeforeMount(() => {
  articleStore.resetArticles();
});

// 获取文章数据
const fetchArticles = async (page = 1) => {
  isLoading.value = true;

  try {
    console.log('获取第', page, '页文章');
    const skip = (page - 1) * pageSize.value;
    const result = await articleStore.fetchArticles({
      skip,
      limit: pageSize.value
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
      console.log('分页信息更新:', pagination.value);

      return result.data;
    }

    // 处理数组响应
    if (Array.isArray(result)) {
      // 更新分页信息（估算）
      pagination.value = {
        total: result.length,
        page: page,
        totalPages: 1
      };

      currentPage.value = page;
      return result;
    }

    return [];
  } catch (error) {
    console.error('获取文章失败:', error);
    notification.error('获取文章失败，请稍后重试');
    return [];
  } finally {
    isLoading.value = false;
    initialDataLoaded.value = true;
  }
};

// 切换页码
const changePage = async (page: number) => {
  if (page < 1 || page > pagination.value.totalPages) return;

  window.scrollTo({ top: 0, behavior: 'smooth' });
  initialDataLoaded.value = false;
  await fetchArticles(page);
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
};

// 处理文章更新
const handleArticleUpdate = async (articleId?: number) => {
  if (articleId) {
    // 如果是当前查看的文章，不需要重新获取详情
    // 因为articleStore.updateArticleStatus已经更新了本地状态
    // 只有在特殊情况下才需要重新获取
    if (currentArticleId.value === articleId && currentView.value === 'detail') {
      // 不再重新获取文章详情，避免页面闪烁
      // await articleStore.fetchArticle(articleId);

      // 触发自定义事件,通知更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } else {
    // 只有在明确需要刷新所有文章时才执行
    // await fetchArticles(currentPage.value);

    // 触发自定义事件,通知更新徽章计数
    document.dispatchEvent(new CustomEvent('update-badge-counts'));
  }
};

// 组件挂载时获取数据
onMounted(async () => {
  await fetchArticles(1);
});

// 监听订阅列表变化，刷新文章列表
watch(() => feedStore.feeds, (newFeeds, oldFeeds) => {
  if (newFeeds.length !== (oldFeeds?.length || 0)) {
    fetchArticles(1);
  }
});
</script>

<template>
  <MainLayout>
    <div class="home-container">
      <!-- 文章列表视图 -->
      <template v-if="currentView === 'list'">
        <div class="home-header">
      <h1 class="page-title">全部文章</h1>

          <div class="header-actions" v-if="articles.length > 0">
              <button
              class="action-btn"
              @click="articleStore.markAllAsRead()"
              :disabled="isLoading || isArticleLoading"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              全部标为已读
              </button>

              <button
              class="action-btn"
              @click="fetchArticles(1)"
              :disabled="isLoading || isArticleLoading"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
              刷新
              </button>
          </div>
        </div>

        <div v-if="isLoading && !initialDataLoaded" class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">正在加载文章...</p>
      </div>

        <ArticleList
          v-else
          :articles="articles"
          :is-loading="isLoading || isArticleLoading"
          :empty-message="feeds.length === 0 ? '您还没有添加任何订阅，请先添加订阅' : '暂无文章'"
          :pagination="pagination"
          @view="viewArticle"
          @update="handleArticleUpdate"
          @change-page="changePage"
        />
      </template>

      <!-- 文章详情视图 -->
      <template v-else-if="currentView === 'detail'">
        <ArticleDetail
          :article-id="currentArticleId!"
          :article="currentArticle"
          :is-loading="isArticleLoading"
          @update="handleArticleUpdate"
          @back="backToList"
        />
      </template>
    </div>
  </MainLayout>
</template>

<style scoped>
.home-container {
  max-width: 100%;
  padding: 1rem;
}

.home-header {
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
  .home-container {
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
</style>
