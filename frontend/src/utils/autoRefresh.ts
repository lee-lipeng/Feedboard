import { watch } from 'vue';
import { usePreferencesStore, type UserPreferences } from '@/stores/preferences';
import { useFeedStore } from '@/stores/feed';
import notification from './notification';

// 模块内的私有变量，用于跟踪定时器和监听器
let timerId: number | null = null;
let stopWatcher: (() => void) | null = null;

/**
 * @description 根据用户偏好设置来启动或重置刷新定时器
 * @param {Partial<UserPreferences>} prefs - 用户的偏好设置对象
 */
function setupTimer(prefs: Partial<UserPreferences>) {
  // 启动新定时器前，先确保清除任何已存在的定时器
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }

  // 检查用户是否启用了自动刷新，并设置了有效的刷新间隔
  if (prefs.auto_refresh_enabled && prefs.refresh_interval) {
    const intervalMinutes = Number(prefs.refresh_interval);
    // 设置一个5分钟的最小刷新间隔，防止过于频繁的请求
    const intervalMilliseconds = Math.max(intervalMinutes, 5) * 60 * 1000;

    timerId = setInterval(() => {
      console.log('正在执行计划中的订阅源刷新...');
      const feedStore = useFeedStore();
      feedStore.triggerRefreshAllFeeds();
      notification.info('订阅源正在后台自动刷新...');
    }, intervalMilliseconds);

    console.log(`自动刷新服务已启动。刷新间隔: ${intervalMinutes} 分钟。`);
  } else {
    console.log('根据用户设置，自动刷新已禁用。');
  }
}

/**
 * @description 初始化自动刷新服务。
 *              此函数只会执行一次初始化，重复调用无效。
 */
export function initializeAutoRefresh() {
  // 如果监听器已存在，说明已经初始化，直接返回，防止重复设置
  if (stopWatcher) {
    return;
  }
  console.log('正在初始化自动刷新服务...');

  const preferencesStore = usePreferencesStore();

  // 监听偏好设置的变化
  stopWatcher = watch(
    () => preferencesStore.preferences,
    (newPrefs) => {
      // 仅当偏好设置已经从后端成功加载后才进行处理
      if (preferencesStore.isInitialized) {
        console.log('用户偏好设置已加载或更新，正在配置定时器...');
        setupTimer(newPrefs);
      }
    },
    {
      deep: true,      // 深度监听以捕捉对象内部属性的变化
      immediate: true, // 立即执行一次回调，用于处理初始状态
    }
  );
}

/**
 * @description 停止自动刷新服务并清理定时器和监听器。
 */
export function stopAutoRefresh() {
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
  if (stopWatcher) {
    // 停止watch监听
    stopWatcher();
    stopWatcher = null;
  }
  console.log('自动刷新服务已停止。');
} 