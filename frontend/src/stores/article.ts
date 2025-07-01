import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api';
import { usePreferencesStore } from './preferences';

// 文章接口
export interface Article {
  id: number;
  title: string;
  url: string;
  author: string | null;
  summary: string | null;
  content: string | null;
  image_url: string | null;
  published_at: string | null;
  guid: string | null;
  feed_id: number;
  feed_title: string;
  is_read: boolean;
  is_favorite: boolean;
  read_later: boolean;
  read_position: number;
  created_at: string;
  updated_at: string;
}

// 文章状态更新接口
export interface ArticleStatusUpdate {
  is_read?: boolean;
  is_favorite?: boolean;
  read_later?: boolean;
  read_position?: number;
}

// 在文件顶部添加分页响应类型
export interface PaginationResponse<T> {
  data: T[];
  total: number;
  page: number;
  totalPages: number;
  hasMore: boolean;
}

export const useArticleStore = defineStore('article', () => {
  // 状态
  const articles = ref<Article[]>([]);
  const searchResults = ref<Article[]>([]);
  const currentArticle = ref<Article | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const lastFetchTime = ref<number>(0);
  const pendingRequest = ref<Promise<any> | null>(null);

  // 缓存有效时间（毫秒）
  const CACHE_DURATION = 60000; // 1分钟

  // 检查缓存是否有效
  const isCacheValid = computed(() => {
    return Date.now() - lastFetchTime.value < CACHE_DURATION;
  });

  const articlesByFeed = ref<Record<number, Article[]>>({});
  const favoriteArticles = ref<Article[]>([]);
  const readLaterArticles = ref<Article[]>([]);
  const unreadArticles = ref<Article[]>([]);
  const latestArticles = ref<Article[]>([]);
  const unreadCount = ref(0);
  const favoriteCount = ref(0);
  const readLaterCount = ref(0);

  // 获取所有文章（带缓存）
  async function fetchArticles(params: { skip?: number; limit?: number; feed_id?: number; is_read?: boolean; is_favorite?: boolean; read_later?: boolean; days_ago?: number; sort?: string; } = {}, replace = true): Promise<PaginationResponse<Article> | Article[]> {
    console.log('开始获取文章, 参数:', params, '替换模式:', replace);

    const preferencesStore = usePreferencesStore();
    // 如果没有传入排序参数，则使用用户设置的默认排序
    const finalParams = {
      ...params,
      sort: params.sort || preferencesStore.preferences.default_sorting || 'newest'
    };

    // 如果已经有一个请求在进行中，等待它完成
    if (pendingRequest.value) {
      try {
        await pendingRequest.value;
      } catch (error) {
        console.error('等待前一个请求时出错:', error);
      }
    }

    // 设置加载状态但延迟显示,避免闪烁
    const loadingTimeout = setTimeout(() => {
      isLoading.value = true;
    }, 200); // 200ms延迟显示加载状态

    // 创建新的请求
    const currentRequest = (async () => {
      try {
        const response = await api.get('/articles', { params: finalParams });
        console.log('API响应:', response.data);

        // 检查响应格式是否包含分页信息
        if (response.data && response.data.data && Array.isArray(response.data.data)) {
          // 新格式，包含分页信息
          const paginatedResponse = response.data as PaginationResponse<Article>;
          console.log('检测到分页响应格式:', {
            total: paginatedResponse.total,
            page: paginatedResponse.page,
            totalPages: paginatedResponse.totalPages,
            articleCount: paginatedResponse.data.length
          });

          if (replace) {
            articles.value = paginatedResponse.data;
            console.log('替换文章列表, 新数量:', paginatedResponse.data.length);
          } else {
            // 合并数据，避免重复
            const newArticles = paginatedResponse.data.filter(
              article => !articles.value.some(a => a.id === article.id)
            );
            articles.value = [...articles.value, ...newArticles];
            console.log('合并文章列表, 原有:', articles.value.length - newArticles.length, '新增:', newArticles.length);
          }

          // 更新缓存时间
          lastFetchTime.value = Date.now();

          return paginatedResponse;
        } else if (Array.isArray(response.data)) {
          // 旧格式，直接返回文章数组
          const articlesData = response.data as Article[];
          console.log('检测到数组响应格式, 文章数量:', articlesData.length);

          if (replace) {
            articles.value = articlesData;
            console.log('替换文章列表, 新数量:', articlesData.length);
          } else {
            // 合并数据，避免重复
            const newArticles = articlesData.filter(
              article => !articles.value.some(a => a.id === article.id)
            );
            articles.value = [...articles.value, ...newArticles];
            console.log('合并文章列表, 原有:', articles.value.length - newArticles.length, '新增:', newArticles.length);
          }

          // 更新缓存时间
          lastFetchTime.value = Date.now();

          return {
            data: articlesData,
            total: articlesData.length,
            page: params.skip ? Math.floor(params.skip / (params.limit || 10)) + 1 : 1,
            totalPages: 1,
            hasMore: articlesData.length === (params.limit || 10)
          };
        }

        console.log('未识别的响应格式, 返回空数据');
        return {
          data: [],
          total: 0,
          page: 1,
          totalPages: 0,
          hasMore: false
        };
      } catch (error) {
        console.error('获取文章失败:', error);
        return {
          data: [],
          total: 0,
          page: 1,
          totalPages: 0,
          hasMore: false
        };
      } finally {
        clearTimeout(loadingTimeout);
        isLoading.value = false;
        pendingRequest.value = null;
      }
    })();

    // 保存当前请求
    pendingRequest.value = currentRequest;

    return currentRequest;
  }

  // 搜索文章
  async function searchArticles(query: string, params: { skip?: number; limit?: number } = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get('/articles/search', {
        params: {
          q: query,
          ...params
        }
      });
      // 假设API返回的格式是 { data: Article[], ...pagination }
      searchResults.value = response.data.data;
      return response.data;
    } catch (err: any) {
      console.error('搜索文章失败:', err);
      error.value = err.response?.data?.detail || '搜索文章失败';
      searchResults.value = [];
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单篇文章详情
  async function fetchArticle(articleId: number) {
    // 1. 尝试从本地缓存（搜索结果或文章列表）中查找文章
    const cachedArticle = searchResults.value.find(a => a.id === articleId) || articles.value.find(a => a.id === articleId);

    if (cachedArticle) {
      currentArticle.value = cachedArticle;
      // 标记为已读（如果尚未标记）
      if (!cachedArticle.is_read) {
        updateArticleStatus(articleId, { is_read: true });
        cachedArticle.is_read = true; // 立即更新UI
      }
      return cachedArticle;
    }

    // 2. 如果缓存中没有，则从API获取
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/articles/${articleId}`);
      currentArticle.value = response.data;

      // 更新列表中的对应文章，如果不存在则添加
      const index = articles.value.findIndex(a => a.id === articleId);
      if (index !== -1) {
        articles.value[index] = response.data;
      } else {
        // 如果文章不在当前列表(例如从搜索页直接跳转)，则将其添加到列表顶部
        articles.value.unshift(response.data);
      }
      
      // 标记为已读（如果尚未标记）
      if (!response.data.is_read) {
        updateArticleStatus(articleId, { is_read: true });
        response.data.is_read = true;
      }

      return response.data;
    } catch (err: any) {
      console.error('获取文章详情失败:', err);
      error.value = err.response?.data?.detail || '获取文章详情失败';
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取文章完整内容
  async function fetchArticleContent(articleId: number): Promise<string | null> {
    try {
      const response = await api.get(`/articles/${articleId}/content`);
      const content = response.data.content;

      // 更新本地文章的 content 字段
      const index = articles.value.findIndex(a => a.id === articleId);
      if (index !== -1) {
        articles.value[index].content = content;
      }
      if (currentArticle.value && currentArticle.value.id === articleId) {
        currentArticle.value.content = content;
      }
      return content;
    } catch (err: any) {
      console.error('获取文章内容失败:', err);
      return null;
    }
  }

  // 更新文章状态
  async function updateArticleStatus(articleId: number, status: ArticleStatusUpdate) {
    error.value = null;

    // 立即在本地更新状态，避免闪烁
    const index = articles.value.findIndex(a => a.id === articleId);
    if (index !== -1) {
      articles.value[index] = {
        ...articles.value[index],
        ...status
      };
    }

    // 如果当前正在查看此文章，也更新当前文章
    if (currentArticle.value && currentArticle.value.id === articleId) {
      currentArticle.value = {
        ...currentArticle.value,
        ...status
      };
    }

    try {
      // 后台发送请求
      const response = await api.patch(`/articles/${articleId}/status`, status);

      // 用服务器返回的完整数据更新本地状态
      if (index !== -1) {
        articles.value[index] = {
          ...articles.value[index],
          ...response.data
        };
      }

      if (currentArticle.value && currentArticle.value.id === articleId) {
        currentArticle.value = {
          ...currentArticle.value,
          ...response.data
        };
      }

      return response.data;
    } catch (err: any) {
      console.error('更新文章状态失败:', err);
      error.value = err.response?.data?.detail || '更新文章状态失败';

      // 请求失败，恢复原状态
      if (index !== -1) {
        // 重新获取文章数据
        try {
          const refreshResponse = await api.get(`/articles/${articleId}`);
          articles.value[index] = refreshResponse.data;

          if (currentArticle.value && currentArticle.value.id === articleId) {
            currentArticle.value = refreshResponse.data;
          }
        } catch (refreshErr) {
          console.error('恢复文章状态失败:', refreshErr);
        }
      }

      return null;
    }
  }

  // 标记所有文章为已读
  async function markAllAsRead(feedId?: number) {
    isLoading.value = true;
    error.value = null;

    try {
      const url = feedId
        ? `/articles/mark-all-read?feed_id=${feedId}`
        : '/articles/mark-all-read';

      const response = await api.post(url);

      // 更新本地缓存中的文章阅读状态
      articles.value = articles.value.map(article => {
        // 如果指定了feed_id，只更新该feed下的文章
        if (feedId === undefined || article.feed_id === feedId) {
          return { ...article, is_read: true };
        }
        return article;
      });

      invalidateCache(); // 强制下次刷新
      return response.data;
    } catch (err: any) {
      console.error('标记所有文章为已读失败:', err);
      error.value = err.response?.data?.detail || '标记所有文章为已读失败';
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // 清除所有文章缓存
  function invalidateCache() {
    lastFetchTime.value = 0;
    articles.value = [];
    currentArticle.value = null;
    articlesByFeed.value = {};
    favoriteArticles.value = [];
    readLaterArticles.value = [];
    unreadArticles.value = [];
    latestArticles.value = [];
  }

  // 根据ID获取文章
  function getArticleById(id: number) {
    return articles.value.find(article => article.id === id) || null;
  }

  // 重置文章列表
  function resetArticles() {
    articles.value = [];
  }

  // 根据feedId清除缓存
  function invalidateCacheForFeed(feedId: number) {
    if (articlesByFeed.value[feedId]) {
      delete articlesByFeed.value[feedId];
      console.log(`Cache for feed ${feedId} invalidated.`);
    }
    // 同时清除可能包含此feed文章的聚合列表
    unreadArticles.value = [];
    latestArticles.value = [];
  }

  async function fetchBadgeCounts() {
    try {
      // 并发请求，提高效率
      const [favoritesResponse, readLaterResponse, unreadResponse] = await Promise.all([
        api.get('/articles', { params: { is_favorite: true, limit: 1 } }),
        api.get('/articles', { params: { read_later: true, limit: 1 } }),
        api.get('/articles', { params: { is_read: false, limit: 1 } }),
      ]);

      if (favoritesResponse.data && 'total' in favoritesResponse.data) {
        favoriteCount.value = favoritesResponse.data.total;
      }
      if (readLaterResponse.data && 'total' in readLaterResponse.data) {
        readLaterCount.value = readLaterResponse.data.total;
      }
      if (unreadResponse.data && 'total' in unreadResponse.data) {
        unreadCount.value = unreadResponse.data.total;
      }
    } catch (error) {
      console.error('获取徽章计数失败:', error);
    }
  }

  return {
    articles,
    searchResults,
    currentArticle,
    isLoading,
    error,
    lastFetchTime,
    isCacheValid,
    articlesByFeed,
    favoriteArticles,
    readLaterArticles,
    unreadArticles,
    latestArticles,
    unreadCount,
    favoriteCount,
    readLaterCount,
    fetchArticles,
    searchArticles,
    fetchArticle,
    fetchArticleContent,
    updateArticleStatus,
    markAllAsRead,
    invalidateCache,
    getArticleById,
    resetArticles,
    invalidateCacheForFeed,
    fetchBadgeCounts,
  };
});
