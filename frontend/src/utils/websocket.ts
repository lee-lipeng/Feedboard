import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useFeedStore } from '@/stores/feed';
import { useArticleStore } from '@/stores/article';
import { useUnreadStore } from '@/stores/unread';
import { usePreferencesStore } from '@/stores/preferences';
import notification from './notification';

const WEBSOCKET_RECONNECT_TIMEOUT = 5000; // 5秒

let socket: WebSocket | null = null;
export const isConnected = ref(false);
let reconnectTimer: number | null = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 5000; // 5 seconds

function getWebSocketURL(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = import.meta.env.DEV
    ? (import.meta.env.VITE_WS_BASE_URL || 'localhost:8000')
    : window.location.host;
  return `${protocol}//${host}/api/ws`;
}

export function connect() {
  const authStore = useAuthStore();
  if (!authStore.token || socket?.readyState === WebSocket.OPEN) {
    console.log('WebSocket connection skipped: No auth token or already connected.');
    return;
  }

  const url = `${getWebSocketURL()}?token=${authStore.token}`;
  socket = new WebSocket(url);

  socket.onopen = () => {
    console.log('WebSocket connection established.');
    isConnected.value = true;
    reconnectAttempts = 0; // Reset attempts on successful connection
  };

  socket.onmessage = async (event) => {
    const feedStore = useFeedStore();
    const articleStore = useArticleStore();
    const unreadStore = useUnreadStore();
    const data = JSON.parse(event.data);

    console.log('WebSocket message received:', data);

    switch (data.type) {
      case 'connection_established':
        notification.success(data.message);
        break;

      case 'feed_processed':
        notification.success(data.message);
        feedStore.fetchFeeds(); // 重新获取feed列表，以更新标题等信息
        articleStore.invalidateCacheForFeed(data.feed_id); // 使该feed的文章缓存失效
        break;

      case 'new_articles':
        notification.info(data.message);
        // 如果有新文章，增加对应feed的未读计数
        if (data.feed_id && data.count > 0) {
          unreadStore.incrementUnreadCount(data.feed_id, data.count);
        }
        articleStore.invalidateCacheForFeed(data.feed_id); // 使该feed的文章缓存失效

        // 检查是否需要发送通知
        const preferencesStore = usePreferencesStore();
        if (preferencesStore.preferences.notifications_enabled) {
          // 确保订阅源列表已加载
          if (feedStore.feeds.length === 0) {
            await feedStore.fetchFeeds();
          }
          const feed = feedStore.feeds.find(f => f.feed_id === data.feed_id);
          const feedTitle = feed ? (feed.title_override || feed.feed_title) : '一个订阅源';

          notification.info(`"${feedTitle}" 有 ${data.count} 篇新文章`);
        }
        break;

      case 'error':
        notification.error(data.message);
        break;

      case 'pong':
        // 用于保持连接，无需处理
        break;
    }
  };

  socket.onclose = () => {
    console.log('WebSocket connection closed.');
    isConnected.value = false;
    socket = null;

    // 只有在用户登录状态下才进行重连
    if (authStore.token && !reconnectTimer) {
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        reconnectTimer = window.setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          connect();
        }, RECONNECT_DELAY);
      } else {
        console.error('WebSocket reconnection failed after several attempts.');
      }
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    // onclose 会被自动调用，所以重连逻辑会在这里触发
  };
}

export function disconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  if (socket) {
    console.log('Disconnecting WebSocket.');
    reconnectAttempts = MAX_RECONNECT_ATTEMPTS; // Prevent reconnection
    socket.close();
    socket = null;
  }
}
