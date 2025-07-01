<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">添加新订阅</h3>
        <button class="close-button" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="close-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="submitForm">
          <!-- 订阅地址 -->
          <div class="form-group">
            <label for="feed-url" class="form-label">RSS 地址 <span class="required">*</span></label>
            <input 
              id="feed-url" 
              v-model="form.url" 
              type="url" 
              class="form-input" 
              :class="{ 'input-error': errors.url }" 
              placeholder="https://example.com/feed.xml"
              required
            />
            <p v-if="errors.url" class="error-message">{{ errors.url }}</p>
            <p class="form-hint">输入RSS订阅源地址，例如：https://news.example.com/rss.xml</p>
          </div>
          
          <!-- 订阅标题 -->
          <div class="form-group">
            <label for="feed-title" class="form-label">订阅标题</label>
            <input 
              id="feed-title" 
              v-model="form.title" 
              type="text" 
              class="form-input" 
              :class="{ 'input-error': errors.title }" 
              placeholder="（可选）自定义标题"
            />
            <p v-if="errors.title" class="error-message">{{ errors.title }}</p>
            <p class="form-hint">留空将使用RSS源提供的标题</p>
          </div>
          
          <!-- 订阅分类 -->
          <div class="form-group">
            <label for="feed-category" class="form-label">分类</label>
            <select 
              id="feed-category" 
              v-model="form.category" 
              class="form-input" 
              :class="{ 'input-error': errors.category }"
            >
              <option v-for="(label, value) in categoryMap" :key="value" :value="value">
                {{ label }}
              </option>
            </select>
            <p v-if="errors.category" class="error-message">{{ errors.category }}</p>
          </div>
          
          <!-- 操作按钮 -->
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeModal">取消</button>
            <button type="submit" class="submit-button" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading-spinner"></span>
              {{ isSubmitting ? '添加中...' : '添加订阅' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { FeedCategory, useFeedStore } from '@/stores/feed';
import notification from '@/utils/notification';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'added']);

const feedStore = useFeedStore();

// 创建分类到中文的映射
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

// 表单数据
const form = reactive({
  url: '',
  title: '',
  category: FeedCategory.OTHER
});

// 表单错误
const errors = reactive({
  url: '',
  title: '',
  category: ''
});

// 提交状态
const isSubmitting = ref(false);

// 重置表单
const resetForm = () => {
  form.url = '';
  form.title = '';
  form.category = FeedCategory.OTHER;
  
  errors.url = '';
  errors.title = '';
  errors.category = '';
};

// 验证表单
const validateForm = () => {
  let isValid = true;
  
  // 验证URL
  if (!form.url) {
    errors.url = 'RSS地址不能为空';
    isValid = false;
  } else if (!isValidUrl(form.url)) {
    errors.url = '请输入有效的URL地址';
    isValid = false;
  } else {
    errors.url = '';
  }
  
  // 验证标题（可选）
  if (form.title && form.title.length > 100) {
    errors.title = '标题不能超过100个字符';
    isValid = false;
  } else {
    errors.title = '';
  }
  
  return isValid;
};

// 验证URL格式
const isValidUrl = (url: string) => {
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
};

// 提交表单
const submitForm = async () => {
  if (!validateForm()) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const newFeed = await feedStore.addFeed({
      url: form.url,
      title: form.title || undefined,
      category: form.category
    });
    
    if (newFeed) {
      notification.success('订阅添加成功！');
      emit('added', newFeed);
      resetForm();
      closeModal();
    } else {
      notification.error(feedStore.error || '添加订阅失败，请稍后重试');
    }
  } catch (error) {
    console.error('添加订阅失败:', error);
    notification.error('添加订阅失败，请稍后重试');
  } finally {
    isSubmitting.value = false;
  }
};

// 关闭对话框
const closeModal = () => {
  emit('close');
};

// 当对话框打开时，重置表单
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    resetForm();
  }
});

// 挂载时添加按ESC键关闭对话框的功能
onMounted(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.isOpen) {
      closeModal();
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  
  return () => {
    window.removeEventListener('keydown', handleKeyDown);
  };
});
</script>

<style scoped>
.modal-overlay {
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

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.close-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1f2937;
  background-color: #f9fafb;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-error {
  border-color: #ef4444;
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.form-hint {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
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

.submit-button {
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

.submit-button:hover:not(:disabled) {
  background-color: #4f46e5;
}

.submit-button:disabled {
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
</style> 