import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api';

// 订阅源分类枚举
export enum FeedCategory {
  NEWS = 'news',
  TECH = 'tech',
  DESIGN = 'design',
  BUSINESS = 'business',
  ENTERTAINMENT = 'entertainment',
  SPORTS = 'sports',
  SCIENCE = 'science',
  HEALTH = 'health',
  BLOG = 'blog',
  OTHER = 'other'
}

// 订阅源接口
export interface Feed {
  id: number;
  title_override: string | null;
  category: FeedCategory;
  created_at: string;
  updated_at: string;
  feed_id: number;
  feed_title: string;
  feed_url: string;
  feed_description: string | null;
  feed_website_url: string | null;
  feed_image_url: string | null;
  feed_last_fetched: string | null;
}

// 新建订阅源接口
export interface FeedCreate {
  url: string;
  title?: string;
  category?: FeedCategory;
}

export const useFeedStore = defineStore('feed', () => {
  // 状态
  const feeds = ref<Feed[]>([]);
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

  // 获取用户所有订阅源（带缓存）
  async function fetchFeeds(forceRefresh = false) {
    // 如果有未完成的请求，等待它完成
    if (pendingRequest.value) {
      return pendingRequest.value;
    }
    
    // 如果缓存有效且不强制刷新，直接返回缓存数据
    if (isCacheValid.value && !forceRefresh && feeds.value.length > 0) {
      return feeds.value;
    }

    isLoading.value = true;
    error.value = null;

    // 创建新请求并保存引用
    pendingRequest.value = api.get('/feeds')
      .then(response => {
        feeds.value = response.data;
        lastFetchTime.value = Date.now();
        return response.data;
      })
      .catch(err => {
        console.error('获取订阅源失败:', err);
        error.value = err.response?.data?.detail || '获取订阅源失败';
        return null;
      })
      .finally(() => {
        isLoading.value = false;
        pendingRequest.value = null;
      });

    return pendingRequest.value;
  }

  // 添加新订阅源
  async function addFeed(feedData: FeedCreate) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/feeds', feedData);
      
      // 添加到列表
      feeds.value.push(response.data);
      
      return response.data;
    } catch (err: any) {
      console.error('添加订阅源失败:', err);
      error.value = err.response?.data?.detail || '添加订阅源失败';
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除订阅源
  async function deleteFeed(feedId: number) {
    isLoading.value = true;
    error.value = null;

    try {
      await api.delete(`/feeds/${feedId}`);
      
      // 从列表中移除
      feeds.value = feeds.value.filter(feed => feed.feed_id !== feedId);
      
      return true;
    } catch (err: any) {
      console.error('删除订阅源失败:', err);
      error.value = err.response?.data?.detail || '删除订阅源失败';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  // 刷新订阅源
  async function refreshFeed(feedId: number) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post(`/feeds/${feedId}/refresh`);
      
      // 更新列表中的项
      const index = feeds.value.findIndex(feed => feed.feed_id === feedId);
      if (index !== -1) {
        feeds.value[index] = {
          ...feeds.value[index],
          ...response.data
        };
      }
      
      return response.data;
    } catch (err: any) {
      console.error('刷新订阅源失败:', err);
      error.value = err.response?.data?.detail || '刷新订阅源失败';
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // 触发为当前用户刷新所有订阅源的后台任务
  async function triggerRefreshAllFeeds() {
    try {
      // 这个操作通常是"即发即忘"，但我们仍然可以处理错误
      await api.post('/feeds/refresh-all');
      // 可以在这里用notification显示一个提示
      console.log('已触发所有订阅源的后台刷新');
      return true;
    } catch (err: any) {
      console.error('触发后台刷新失败:', err);
      // 可以在这里用notification显示一个错误提示
      return false;
    }
  }

  // 重置缓存，强制下次请求从服务器获取最新数据
  function invalidateCache() {
    lastFetchTime.value = 0;
  }

  function getFeedById(id: number): Feed | undefined {
    return feeds.value.find(feed => feed.feed_id === id);
  }

  return {
    feeds,
    isLoading,
    error,
    isCacheValid,
    fetchFeeds,
    addFeed,
    deleteFeed,
    refreshFeed,
    invalidateCache,
    getFeedById,
    triggerRefreshAllFeeds
  };
}); 