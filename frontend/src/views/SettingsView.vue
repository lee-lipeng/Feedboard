<template>
  <MainLayout>
    <div class="settings-container">
      <h1 class="page-title">设置</h1>

      <div class="settings-content">
        <!-- 应用设置卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h2 class="card-title">应用设置</h2>
          </div>
          <div v-if="!isInitialized" class="card-body">加载中...</div>
          <div v-else class="card-body">
            <div class="settings-section">
              <div class="settings-group">
                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">通知设置</h3>
                    <p class="item-description">接收新文章通知、订阅更新等消息</p>
                  </div>
                  <label class="switch">
                    <input type="checkbox" v-model="localPreferences.notifications_enabled" @change="save">
                    <span class="slider round"></span>
                  </label>
                </div>

                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">自动刷新</h3>
                    <p class="item-description">定期自动检查订阅源更新</p>
                  </div>
                  <label class="switch">
                    <input type="checkbox" v-model="localPreferences.auto_refresh_enabled" @change="save">
                    <span class="slider round"></span>
                  </label>
                </div>

                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">刷新频率</h3>
                    <p class="item-description">设置自动检查订阅更新的频率</p>
                  </div>
                  <select class="settings-select" v-model="localPreferences.refresh_interval" :disabled="!localPreferences.auto_refresh_enabled" @change="save">
                    <option value="15">每15分钟</option>
                    <option value="30">每30分钟</option>
                    <option value="60">每小时</option>
                    <option value="360">每6小时</option>
                    <option value="720">每12小时</option>
                    <option value="1440">每天</option>
                  </select>
                </div>

                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">默认排序方式</h3>
                    <p class="item-description">设置文章列表的默认排序方式</p>
                  </div>
                  <select class="settings-select" v-model="localPreferences.default_sorting" @change="save">
                    <option value="newest">最新发布</option>
                    <option value="oldest">最早发布</option>
                    <option value="source">按来源</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 阅读偏好设置卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h2 class="card-title">阅读偏好</h2>
          </div>
          <div v-if="!isInitialized" class="card-body">加载中...</div>
          <div v-else class="card-body">
            <div class="settings-section">
              <div class="settings-group">
                <div class="settings-item">
                  <span class="item-title">字体大小</span>
                  <div class="slider-group">
                    <input
                      type="range"
                      min="80"
                      max="120"
                      step="10"
                      v-model="localPreferences.font_size"
                      class="preference-slider"
                      @change="save"
                    />
                    <span class="slider-value">{{ localPreferences.font_size }}%</span>
                  </div>
                </div>

                <div class="settings-item">
                  <span class="item-title">最近文章天数</span>
                  <div class="slider-group">
                    <input
                      type="range"
                      min="1"
                      max="30"
                      step="1"
                      v-model="localPreferences.latest_articles_days"
                      class="preference-slider"
                      @change="save"
                    />
                    <span class="slider-value">{{ localPreferences.latest_articles_days }} 天</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据管理卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h2 class="card-title">数据管理</h2>
          </div>

          <div class="card-body">
            <div class="settings-section">
              <div class="settings-group">
                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">导出数据</h3>
                    <p class="item-description">导出您的订阅源、收藏文章等数据</p>
                  </div>
                  <button class="action-btn" @click="exportData" :disabled="isExporting">
                    <svg v-if="!isExporting" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    <span v-if="isExporting" class="loading-spinner-small"></span>
                    {{ isExporting ? '导出中...' : '导出' }}
                  </button>
                </div>

                <div class="settings-item">
                  <div class="item-info">
                    <h3 class="item-title">导入数据</h3>
                    <p class="item-description">从备份文件导入订阅源和设置</p>
                  </div>
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileImport"
                    style="display: none"
                    accept=".opml,.xml"
                  />
                  <button class="action-btn" @click="triggerFileInput" :disabled="isImporting">
                    <svg v-if="!isImporting" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                    <span v-if="isImporting" class="loading-spinner-small"></span>
                    {{ isImporting ? '导入中...' : '导入' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 账户管理卡片 -->
        <div class="settings-card">
          <div class="card-header">
            <h2 class="card-title">账户管理</h2>
          </div>

          <div class="card-body">
            <div class="settings-section">
              <div class="settings-group">
                <div class="settings-item danger-zone">
                  <div class="item-info">
                    <h3 class="item-title danger-text">删除账户</h3>
                    <p class="item-description">永久删除您的账户和所有相关数据</p>
                  </div>
                  <button class="action-btn danger" @click="showDeleteAccountConfirm = true">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="action-icon">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                    </svg>
                    删除账户
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 确认对话框 - 删除账户 -->
      <div v-if="showDeleteAccountConfirm" class="confirm-dialog-backdrop">
        <div class="confirm-dialog">
          <div class="confirm-header">
            <h3>确认删除账户</h3>
          </div>
          <div class="confirm-body">
            <p>您确定要删除您的账户吗？所有数据将被永久删除，此操作无法撤销。</p>
            <div class="confirm-input-group">
              <label for="confirm-delete">请输入您的邮箱确认：</label>
              <input type="email" id="confirm-delete" v-model="deleteConfirmEmail" placeholder="输入您的邮箱地址" />
            </div>
          </div>
          <div class="confirm-actions">
            <button class="cancel-btn" @click="showDeleteAccountConfirm = false">取消</button>
            <button
              class="confirm-btn danger"
              @click="deleteAccount"
              :disabled="deleteConfirmEmail !== userEmail"
            >永久删除</button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { usePreferencesStore, type UserPreferences } from '@/stores/preferences';
import { storeToRefs } from 'pinia';
import notification from '@/utils/notification';
import api from '@/api';

// 简单的防抖函数
function debounce<F extends (...args: any[]) => any>(func: F, waitFor: number) {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  const debounced = (...args: Parameters<F>) => {
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), waitFor);
  };

  return debounced;
}

const authStore = useAuthStore();
const router = useRouter();
const preferencesStore = usePreferencesStore();
const { preferences, isLoading, isInitialized } = storeToRefs(preferencesStore);

// 用户信息
const userEmail = computed(() => authStore.user?.email || '');

// 创建一个本地的响应式对象，用于表单绑定
const localPreferences = ref<UserPreferences>({} as UserPreferences);

// 监听store的变化，更新本地副本
watch(preferences, (newPrefs) => {
  if (newPrefs) {
    localPreferences.value = JSON.parse(JSON.stringify(newPrefs));
  }
}, { deep: true, immediate: true });


// 防抖的保存函数
const debouncedSave = debounce(async (prefs: UserPreferences) => {
  // 仅当 prefs 真正存在时才保存
  if (!prefs || Object.keys(prefs).length === 0) {
    return;
  }
  const result = await preferencesStore.saveAllPreferences(prefs);
  if (result) {
    notification.success('设置已自动保存');
  } else {
    notification.error('保存失败，请稍后重试');
  }
}, 800);

const save = () => {
  if (!isInitialized.value) return;

  const prefsToSave = JSON.parse(JSON.stringify(localPreferences.value));

  // v-model can return strings for number inputs, ensure they are numbers
  prefsToSave.font_size = Number(prefsToSave.font_size);
  prefsToSave.latest_articles_days = Number(prefsToSave.latest_articles_days);
  prefsToSave.refresh_interval = Number(prefsToSave.refresh_interval);

  debouncedSave(prefsToSave);
};


// 确认对话框状态
const showDeleteAccountConfirm = ref(false);
const deleteConfirmEmail = ref('');
const isExporting = ref(false);
const isImporting = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click();
};

// 处理文件导入
const handleFileImport = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  isImporting.value = true;
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/data/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    notification.success(response.data.message || '导入任务已开始，请稍后查看结果。');
  } catch (error: any) {
    notification.error(error.response?.data?.detail || '导入失败，请检查文件格式或稍后再试。');
  } finally {
    isImporting.value = false;
    // 重置file input，以便可以再次上传同一个文件
    if (fileInput.value) {
      fileInput.value.value = '';
    }
  }
};

// 导出数据
const exportData = async () => {
  isExporting.value = true;
  try {
    const response = await api.get('/data/export', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    // 从响应头中获取文件名
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'feedboard_subscriptions.opml'; // 默认文件名
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1];
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    notification.success('数据导出成功！');
  } catch (error) {
    notification.error('数据导出失败，请稍后重试。');
  } finally {
    isExporting.value = false;
  }
};


// 删除账户
const deleteAccount = async () => {
  if (deleteConfirmEmail.value !== userEmail.value) {
    return;
  }

  try {
    // 调用删除账户
    await authStore.deleteAccount();
    notification.success('账号删除成功');
    showDeleteAccountConfirm.value = false;
    await authStore.logout();
  } catch (error: any) {
    notification.error(error.response?.data?.detail || '账号删除失败，请稍后重试');
  }
};

onMounted(() => {
  preferencesStore.fetchPreferences();
});
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 2rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

/* 内容区 */
.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 卡片样式 */
.settings-card {
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.card-body {
  padding: 1.5rem;
}

/* 设置区域 */
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.settings-group {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f3f4f6;
}

.settings-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.item-description {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
}

/* 开关按钮样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e7eb;
  transition: 0.2s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.2s;
}

input:checked + .slider {
  background-color: #6366f1;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}

/* 下拉选择框 */
.settings-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1f2937;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.settings-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.settings-select:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.75;
}

/* 操作按钮 */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.75rem;
  background-color: #f3f4f6;
  border: none;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #e5e7eb;
  color: #1f2937;
}

.action-btn.danger {
  background-color: #fee2e2;
  color: #ef4444;
}

.action-btn.danger:hover {
  background-color: #fecaca;
}

.action-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

/* 保存按钮 */
.form-actions-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.save-btn:hover:not(:disabled) {
  background-color: #4f46e5;
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 危险区域 */
.danger-zone {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #f87171;
}

.danger-text {
  color: #ef4444;
}

/* 确认对话框 */
.confirm-dialog-backdrop {
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

.confirm-dialog {
  width: 90%;
  max-width: 400px;
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  animation: dialogFadeIn 0.2s ease;
}

@keyframes dialogFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.confirm-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.confirm-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.confirm-body {
  padding: 1.5rem;
}

.confirm-body p {
  font-size: 0.9375rem;
  color: #4b5563;
  margin: 0 0 1rem 0;
}

.confirm-input-group {
  margin-top: 1rem;
}

.confirm-input-group label {
  display: block;
  font-size: 0.875rem;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.confirm-input-group input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1f2937;
}

.confirm-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-btn {
  padding: 0.5rem 0.75rem;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #4b5563;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #f9fafb;
}

.confirm-btn {
  padding: 0.5rem 0.75rem;
  background-color: #6366f1;
  border: none;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #4f46e5;
}

.confirm-btn.danger {
  background-color: #ef4444;
}

.confirm-btn.danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.confirm-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 响应式调整 */
@media (min-width: 768px) {
  .page-title {
    font-size: 1.75rem;
    margin-bottom: 2rem;
  }

  .card-header {
    padding: 1.5rem 2rem;
  }

  .card-title {
    font-size: 1.25rem;
  }

  .card-body {
    padding: 2rem;
  }

  .item-title {
    font-size: 1rem;
  }

  .item-description {
    font-size: 0.875rem;
  }
}

.slider-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 200px;
}

.preference-slider {
  flex: 1;
  height: 5px;
  background: #e5e7eb;
  border-radius: 5px;
  appearance: none;
  outline: none;
}

.preference-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #6366f1;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preference-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #6366f1;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.slider-value {
  font-size: 0.75rem;
  color: #6b7280;
  width: 40px;
  text-align: right;
}

.loading-spinner-small {
  width: 0.875rem;
  height: 0.875rem;
  border: 2px solid rgba(75, 85, 99, 0.2);
  border-radius: 50%;
  border-top-color: #4b5563;
  animation: spin 0.8s linear infinite;
  margin-right: 0.5rem;
}
</style>
