<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AuthLayout from '@/components/layout/AuthLayout.vue';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref<string | null>(null);
const isLoading = ref(false);
const successMessage = ref<string | null>(null);

const handleRegister = async () => {
  error.value = null;
  successMessage.value = null;

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致。';
    return;
  }

  isLoading.value = true;
  try {
    await authStore.register(email.value, password.value);
    successMessage.value = '注册成功！正在跳转至登录页面...';
    // store 中已有跳转逻辑
  } catch (err: any) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <AuthLayout>
    <h1 class="auth-title">创建账户</h1>
    <p class="auth-subtitle">
      注册以开始使用
    </p>

    <form @submit.prevent="handleRegister" class="auth-form">
      <div class="input-group">
        <div class="input-wrapper">
          <input
            id="email-register"
            v-model="email"
            type="email"
            placeholder="邮箱地址"
            class="auth-input"
            required
          />
        </div>

        <div class="input-wrapper">
          <input
            id="password-register"
            v-model="password"
            type="password"
            placeholder="密码"
            class="auth-input"
            required
          />
        </div>

        <div class="input-wrapper">
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            placeholder="确认密码"
            class="auth-input"
            required
          />
        </div>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="successMessage" class="success-message">{{ successMessage }}</div>

      <button type="submit" class="auth-button" :disabled="isLoading">
        <span v-if="isLoading" class="loading-spinner"></span>
        <span>{{ isLoading ? '创建中...' : '创建账户' }}</span>
      </button>
    </form>

    <div class="auth-footer">
      <p>
        已经有账户了？
        <RouterLink to="/login" class="auth-link">登录</RouterLink>
      </p>
    </div>
  </AuthLayout>
</template>

<style scoped>
.auth-title {
  margin-bottom: 0.75rem;
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: #1f2937;
  text-align: center;
}

.auth-subtitle {
  margin-bottom: 2rem;
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}

.auth-form {
  margin-bottom: 1.5rem;
  width: 100%;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-wrapper {
  margin-bottom: 1rem;
  position: relative;
}

.auth-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(209, 213, 219, 0.8);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #1f2937;
  outline: none;
  transition: all 0.2s ease;
}

.auth-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background-color: rgba(255, 255, 255, 1);
}

.auth-input::placeholder {
  color: #9ca3af;
}

.error-message {
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #ef4444;
  text-align: center;
}

.success-message {
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #10b981;
  text-align: center;
}

.auth-button {
  position: relative;
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.auth-button:disabled {
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

.auth-footer {
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
  margin-top: 1.5rem;
}

.auth-link {
  color: #6366f1;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}

.auth-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* 媒体查询 - 桌面端字体大小调整 */
@media (min-width: 1024px) {
  .auth-title {
    font-size: 2rem;
    margin-top: 0.5rem;
  }
  
  .auth-subtitle {
    font-size: 1rem;
    margin-bottom: 2.5rem;
  }
  
  .auth-input {
    font-size: 0.9375rem;
    padding: 0.875rem 1.25rem;
  }
  
  .auth-button {
    font-size: 0.9375rem;
    padding: 0.875rem 1.5rem;
    margin-top: 0.5rem;
  }
  
  .auth-footer {
    margin-top: 2rem;
  }
}

/* 平板设备 */
@media (min-width: 768px) and (max-width: 1023px) {
  .auth-title {
    font-size: 1.875rem;
  }
  
  .auth-subtitle {
    font-size: 0.9375rem;
  }
  
  .auth-button {
    padding: 1rem 1.5rem;
  }
}

/* 大型显示器 */
@media (min-width: 1280px) {
  .auth-title {
    font-size: 2.25rem;
  }
  
  .auth-subtitle {
    font-size: 1.125rem;
  }
  
  .auth-form {
    margin-bottom: 2rem;
  }
  
  .auth-input {
    padding: 1rem 1.25rem;
    font-size: 1rem;
  }
  
  .auth-button {
    font-size: 1rem;
    padding: 1rem 1.5rem;
  }
}
</style> 