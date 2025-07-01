import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 15000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证信息
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 调试日志
    console.log(`API请求: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.params || config.data);
    
    return config;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    // 调试日志
    console.log(`API响应: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      dataSize: typeof response.data === 'object' ? 
        (Array.isArray(response.data) ? response.data.length : Object.keys(response.data).length) : 
        'non-object'
    });
    
    return response;
  },
  (error) => {
    console.error('API响应错误:', error.response || error);
    
    // 处理401错误 - 未授权
    if (error.response && error.response.status === 401) {
      // 清除token并重定向到登录页
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default api; 