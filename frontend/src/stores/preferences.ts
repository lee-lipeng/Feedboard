import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api';

// 接口定义
export interface UserPreferences {
  // 阅读偏好
  font_size: number;
  latest_articles_days: number;
  // 应用设置
  notifications_enabled: boolean;
  auto_refresh_enabled: boolean;
  refresh_interval: number;
  default_sorting: string;
}

export const usePreferencesStore = defineStore('preferences', () => {
  // 状态：为所有偏好设置提供初始默认值
  const preferences = ref<Partial<UserPreferences>>({
    font_size: 100,
    latest_articles_days: 7,
    notifications_enabled: true,
    auto_refresh_enabled: true,
    refresh_interval: 60,
    default_sorting: 'newest',
  });
  
  const isLoading = ref(false);
  const isInitialized = ref(false);

  // 从服务器获取偏好设置
  async function fetchPreferences() {
    if (isInitialized.value) return; // 防止重复获取
    isLoading.value = true;
    try {
      const response = await api.get<UserPreferences>('/preferences');
      preferences.value = response.data;
      isInitialized.value = true;
      applyPreferences(response.data); // 应用加载的设置
    } catch (error) {
      console.error('获取用户偏好设置失败:', error);
      // 在出错时也应该抛出异常，以便调用者可以捕获
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  // 保存所有偏好设置到服务器
  async function saveAllPreferences(newPreferences: UserPreferences) {
    isLoading.value = true;
    try {
      const response = await api.put<UserPreferences>('/preferences', newPreferences);
      preferences.value = response.data; // 更新本地状态为服务器返回的最新状态
      applyPreferences(response.data); // 应用新设置
      return true;
    } catch (error) {
      console.error('更新用户偏好设置失败:', error);
      // 可选：将状态回滚到保存前的状态
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  // 应用设置到页面（例如，字体大小）
  function applyPreferences(prefs: UserPreferences) {
    if (prefs.font_size) {
      document.documentElement.style.fontSize = `${prefs.font_size}%`;
    }
    // 其他需要立即生效的设置可在此添加
  }

  return {
    preferences,
    isLoading,
    isInitialized,
    fetchPreferences,
    saveAllPreferences,
  };
});
