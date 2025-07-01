<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AuthLayout from '@/components/layout/AuthLayout.vue';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const error = ref<string | null>(null);
const isLoading = ref(false);

const handleLogin = async () => {
  error.value = null;
  isLoading.value = true;
  try {
    await authStore.login(email.value, password.value);
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查您的邮箱或密码。';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <AuthLayout>
    <h1 class="auth-title">欢迎回来</h1>
    <p class="auth-subtitle">
      登录到您的账户
    </p>

    <form @submit.prevent="handleLogin" class="auth-form">
      <div class="input-group">
        <div class="input-wrapper">
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="邮箱地址"
            class="auth-input"
            required
            autocomplete="email"
          />
        </div>

        <div class="input-wrapper">
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="密码"
            class="auth-input"
            required
            autocomplete="current-password"
          />
        </div>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>

      <button type="submit" class="auth-button" :disabled="isLoading">
        <span v-if="isLoading" class="loading-spinner"></span>
        <span>{{ isLoading ? '登录中...' : '登录' }}</span>
      </button>
    </form>

    <div class="auth-footer">
      <p>
        还没有账户？
        <RouterLink to="/register" class="auth-link">注册</RouterLink>
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