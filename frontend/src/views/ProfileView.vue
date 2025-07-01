<template>
  <MainLayout>
    <div class="profile-container">
      <h1 class="page-title">个人中心</h1>

      <div class="profile-content">
        <!-- 用户信息卡片 -->
        <div class="profile-card">
          <div class="card-header">
            <h2 class="card-title">个人信息</h2>
          </div>

          <div class="card-body">
            <!-- 头像区域 - 自动根据邮箱生成 -->
            <div class="avatar-section">
              <div class="avatar-container">
                <div class="avatar-placeholder">
                  <span>{{ userInitials }}</span>
                </div>
              </div>
            </div>

            <!-- 用户信息表单 -->
            <div class="form-section">
              <div class="form-group">
                <label for="email" class="form-label">邮箱</label>
                <input
                  type="email"
                  id="email"
                  class="form-input"
                  :class="{ 'input-error': emailTouched && !isValidEmail(email) }"
                  v-model="email"
                  placeholder="请输入新的邮箱地址"
                  @blur="emailTouched = true"
                  @input="validateEmail"
                />
                <p v-if="emailTouched && !isValidEmail(email)" class="form-error">请输入有效的邮箱地址</p>
                <p class="form-hint">修改邮箱后需要重新登录</p>
              </div>

              <div class="form-actions">
                <button
                  class="save-btn"
                  @click="updateEmail"
                  :disabled="isSaving || email === authStore.user?.email || !isValidEmail(email)"
                >
                  <span v-if="isSaving" class="loading-spinner"></span>
                  {{ isSaving ? '保存中...' : '修改邮箱' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全设置卡片 -->
        <div class="profile-card">
          <div class="card-header">
            <h2 class="card-title">安全设置</h2>
          </div>

          <div class="card-body">
            <div class="form-section">
              <div class="form-group">
                <label for="new-password" class="form-label">新密码</label>
                <input
                  type="password"
                  id="new-password"
                  class="form-input"
                  :class="{ 'input-error': newPasswordTouched && (!newPassword || !isStrongPassword) }"
                  v-model="newPassword"
                  placeholder="请输入新密码"
                  @blur="newPasswordTouched = true"
                  @input="validatePassword"
                />
                <p v-if="newPasswordTouched && !newPassword" class="form-error">请输入新密码</p>
                <p v-if="newPasswordTouched && newPassword && !isStrongPassword" class="form-error">
                  密码强度不足，需至少8位并包含数字和字母
                </p>

                <!-- 密码强度指示器 -->
                <div v-if="newPassword" class="password-strength">
                  <div class="strength-bar">
                    <div
                      class="strength-progress"
                      :style="{ width: passwordStrength + '%' }"
                      :class="{
                        'strength-weak': passwordStrength < 40,
                        'strength-medium': passwordStrength >= 40 && passwordStrength < 80,
                        'strength-strong': passwordStrength >= 80
                      }"
                    ></div>
                  </div>
                  <span class="strength-text">
                    {{
                      passwordStrength < 40 ? '弱' :
                      passwordStrength < 80 ? '中' : '强'
                    }}
                  </span>
                </div>
              </div>

              <div class="form-group">
                <label for="confirm-password" class="form-label">确认新密码</label>
                <input
                  type="password"
                  id="confirm-password"
                  class="form-input"
                  :class="{ 'input-error': confirmPasswordTouched && (!confirmPassword || newPassword !== confirmPassword) }"
                  v-model="confirmPassword"
                  placeholder="请再次输入新密码"
                  @blur="confirmPasswordTouched = true"
                  @input="validatePassword"
                />
                <p v-if="confirmPasswordTouched && !confirmPassword" class="form-error">请再次输入新密码</p>
                <p v-if="confirmPasswordTouched && confirmPassword && newPassword !== confirmPassword" class="form-error">两次输入的密码不一致</p>
                <p class="form-hint">修改密码后需要重新登录</p>
              </div>

              <div class="form-actions">
                <button
                  class="save-btn"
                  @click="changePassword"
                  :disabled="isChangingPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword || !isStrongPassword"
                >
                  <span v-if="isChangingPassword" class="loading-spinner"></span>
                  {{ isChangingPassword ? '修改中...' : '修改密码' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import { useAuthStore } from '@/stores/auth';
import { usePreferencesStore } from '@/stores/preferences';
import { useRouter } from 'vue-router';
import notification from '@/utils/notification';

const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();
const router = useRouter();

// 用户基本信息
const email = ref(authStore.user?.email || '');
const userInitials = computed(() => {
  if (!authStore.user?.email) return '?';
  return authStore.user.email.charAt(0).toUpperCase();
});

// 修改密码相关
const newPassword = ref('');
const confirmPassword = ref('');

// 计算密码强度
const passwordStrength = computed(() => {
  if (!newPassword.value) return 0;

  let strength = 0;

  // 长度分数，最大 40 分
  strength += Math.min(newPassword.value.length * 5, 40);

  // 包含数字，额外 20 分
  if (/\d/.test(newPassword.value)) strength += 20;

  // 包含小写字母，额外 15 分
  if (/[a-z]/.test(newPassword.value)) strength += 15;

  // 包含大写字母，额外 15 分
  if (/[A-Z]/.test(newPassword.value)) strength += 15;

  // 包含特殊字符，额外 10 分
  if (/[^a-zA-Z0-9]/.test(newPassword.value)) strength += 10;

  return Math.min(strength, 100);
});

// 判断密码是否足够强
const isStrongPassword = computed(() => {
  // 要求至少8位，且至少包含数字和字母
  return newPassword.value.length >= 8 &&
    /\d/.test(newPassword.value) &&
    /[a-zA-Z]/.test(newPassword.value);
});

// 表单状态
const isSaving = ref(false);
const isChangingPassword = ref(false);

// 表单验证状态
const emailTouched = ref(false);
const newPasswordTouched = ref(false);
const confirmPasswordTouched = ref(false);

// 验证邮箱格式
const isValidEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 邮箱验证
const validateEmail = () => {
  if (email.value.trim()) {
    emailTouched.value = true;
  }
};

// 密码验证
const validatePassword = () => {
  if (newPassword.value) {
    newPasswordTouched.value = true;
  }

  if (confirmPassword.value) {
    confirmPasswordTouched.value = true;
  }
};

// 更新邮箱
const updateEmail = async () => {
  emailTouched.value = true;

  if (!email.value.trim()) {
    notification.error('请输入邮箱地址');
    return;
  }

  if (email.value === authStore.user?.email) {
    notification.warning('邮箱地址未修改');
    return;
  }

  if (!isValidEmail(email.value)) {
    notification.error('请输入有效的邮箱地址');
    return;
  }

  isSaving.value = true;

  try {
    // 调用API更新邮箱
    await authStore.updateEmail(email.value);
    notification.success('邮箱修改成功，正在跳转到登录页面...');
    setTimeout(async () => {
      await authStore.logout();
      router.push({ name: 'login' });
    }, 1000);
  } catch (error: any) {
    notification.error(error.response?.data?.detail || '修改失败，请稍后重试');
    isSaving.value = false;
  }
};

// 修改密码
const changePassword = async () => {
  newPasswordTouched.value = true;
  confirmPasswordTouched.value = true;

  if (!newPassword.value || !confirmPassword.value) {
    notification.error('请填写所有密码字段');
    return;
  }

  if (!isStrongPassword.value) {
    notification.error('密码强度不足，需至少8位并包含数字和字母');
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    notification.error('两次输入的新密码不一致');
    return;
  }

  isChangingPassword.value = true;

  try {
    // 调用API更新密码，不再需要旧密码
    await authStore.updatePassword(newPassword.value);
    notification.success('密码修改成功，正在跳转到登录页面...');
    setTimeout(async () => {
      await authStore.logout();
      router.push({ name: 'login' });
    }, 1000);
  } catch (error: any) {
    notification.error(error.response?.data?.detail || '修改失败，请稍后重试');
    isChangingPassword.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

/* 内容区 */
.profile-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 卡片样式 */
.profile-card {
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

/* 头像区域 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 600;
}

/* 表单区域 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1f2937;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input.input-error {
  border-color: #ef4444;
}

.form-input.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-error {
  font-size: 0.75rem;
  color: #ef4444;
  margin: 0.25rem 0 0 0;
}

.form-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0.25rem 0 0 0;
  font-style: italic;
}

/* 密码强度指示器 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-progress {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.strength-weak {
  background-color: #ef4444;
}

.strength-medium {
  background-color: #f59e0b;
}

.strength-strong {
  background-color: #10b981;
}

.strength-text {
  font-size: 0.75rem;
  color: #6b7280;
  min-width: 24px;
}

.form-actions {
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
}
</style>
