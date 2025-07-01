import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api';
import router from '@/router';
import { connect, disconnect } from '@/utils/websocket';

// 根据后端 User_Pydantic 模型定义用户接口
interface User {
  id: number;
  email: string;
}

// 用于更新用户信息的接口
interface UserUpdate {
  email?: string;
  password?: string;
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('access_token'));

  // 计算属性：判断用户是否已认证
  const isAuthenticated = computed(() => !!token.value);

  // 封装设置token的逻辑，以便重用
  function setToken(accessToken: string | null) {
    if (accessToken) {
      token.value = accessToken;
      localStorage.setItem('access_token', accessToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    } else {
      token.value = null;
      localStorage.removeItem('access_token');
      delete api.defaults.headers.common['Authorization'];
    }
  }

  // 登录
  async function login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    const { access_token } = response.data;
    setToken(access_token);
    
    await fetchUser();
    connect(); // 登录成功后建立连接
    await router.push({ name: 'home' });
  }

  // 注册新用户
  async function register(email: string, password: string) {
    const response = await api.post('/auth/register', { email, password });
    // 注册成功后，通常会让用户去登录，或者直接返回token并自动登录
    // 这里我们引导用户去登录页面
    await router.push({ name: 'login' });
    // 可以添加一个提示，例如使用一个状态来通知UI显示"注册成功，请登录"
  }

  // 获取当前用户信息
  async function fetchUser() {
    if (token.value) {
      try {
        const response = await api.get<User>('/users/me');
        user.value = response.data;
      } catch (error) {
        // 如果获取用户信息失败（例如token过期），则登出
        console.error("获取用户信息失败, 可能token已过期。", error);
        logout();
      }
    }
  }

  // 更新用户邮箱
  async function updateEmail(newEmail: string) {
    if (!token.value) {
      throw new Error('用户未登录');
    }
    
    const userData: UserUpdate = { email: newEmail };
    const response = await api.put('/users/me', userData);
    return response.data;
  }

  // 更新用户密码
  async function updatePassword(newPassword: string) {
    if (!token.value) {
      throw new Error('用户未登录');
    }
    
    const userData: UserUpdate = { password: newPassword };
    const response = await api.put('/users/me', userData);
    return response.data;
  }

  // 登出
  function logout() {
    disconnect(); // 登出时断开连接
    setToken(null);
    user.value = null;
    router.push({ name: 'login' });
  }

  // 应用初始化时检查认证状态并连接
  async function checkAuthAndConnect() {
    if (isAuthenticated.value) {
      await fetchUser();
      // 确保在获取用户信息成功（即用户仍然有效）后才连接
      if (user.value) {
        connect();
      }
    }
  }

  // 初始化时立即执行
  checkAuthAndConnect();

  return { 
    user, 
    token, 
    isAuthenticated,
    login, 
    register, 
    fetchUser, 
    updateEmail, 
    updatePassword, 
    logout,
    checkAuthAndConnect,
  };
}); 