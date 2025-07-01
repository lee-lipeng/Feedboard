<template>
  <div class="auth-container">
    <!-- 背景元素 -->
    <div class="auth-blur-circle circle-1"></div>
    <div class="auth-blur-circle circle-2"></div>
    <div class="auth-blur-circle circle-3"></div>
    
    <!-- 水平两栏布局容器 -->
    <div class="auth-content-wrapper">
      <!-- 左侧登录/注册表单面板 -->
      <div class="auth-card">
        <div class="logo-container">
          <img src="@/assets/logo.svg" alt="Feedboard Logo" class="auth-logo" />
        </div>
        <div class="card-content">
          <slot></slot>
        </div>
      </div>
      
      <!-- 右侧装饰面板 - 仅在桌面显示 -->
      <div class="auth-decoration">
        <div class="decoration-card">
          <div class="decoration-content">
            <h2>Feedboard</h2>
            <p>您的个性化RSS阅读体验</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 该组件是一个纯布局组件，目前不需要脚本逻辑。
</script>

<style>
/* 使用系统UI字体 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica,
    Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 认证页面容器 */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  background: #f5f5f7;
  /* 以下用于创建微妙的渐变背景 */
  background-image: linear-gradient(
    to bottom right,
    rgba(255, 255, 255, 0.9),
    rgba(245, 245, 247, 0.9)
  );
}

/* 水平两栏布局容器 */
.auth-content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 1200px;
  width: 100%;
  position: relative;
  z-index: 5;
  gap: 2rem;
}

/* 背景模糊圆形 - 创造视觉趣味 */
.auth-blur-circle {
  position: fixed;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.6;
  z-index: 1;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -5%;
  right: 15%;
  background: rgba(125, 211, 252, 0.4); /* 浅蓝色 */
  animation: float 8s infinite ease-in-out;
}

.circle-2 {
  width: 350px;
  height: 350px;
  bottom: -10%;
  left: 10%;
  background: rgba(190, 242, 100, 0.3); /* 浅绿色 */
  animation: float 12s infinite ease-in-out;
}

.circle-3 {
  width: 250px;
  height: 250px;
  top: 40%;
  left: 30%;
  background: rgba(251, 113, 133, 0.2); /* 浅红色 */
  animation: float 10s infinite ease-in-out reverse;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-20px) scale(1.05);
  }
}

/* 卡片容器 */
.auth-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.05),
    0 8px 32px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transform: translateY(0);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.8);
  z-index: 10;
  height: fit-content;
}

.auth-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 8px 30px rgba(0, 0, 0, 0.08),
    0 12px 40px rgba(0, 0, 0, 0.08);
}

/* Logo 容器 */
.logo-container {
  display: flex;
  justify-content: center;
  padding: 2rem 0 0.5rem;
}

.auth-logo {
  width: 60px;
  height: 60px;
}

/* 卡片内容 */
.card-content {
  padding: 1.5rem 2.5rem 2.5rem;
}

/* 右侧装饰面板 */
.auth-decoration {
  display: none; /* 移动端默认隐藏 */
  flex-shrink: 0;
}

.decoration-card {
  width: 400px;
  height: 480px;
  background: rgba(99, 102, 241, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.03),
    0 8px 32px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.decoration-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 8px 30px rgba(0, 0, 0, 0.06),
    0 12px 40px rgba(0, 0, 0, 0.06);
}

.decoration-content {
  text-align: center;
  padding: 2rem;
  z-index: 2;
}

.decoration-content h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
}

.decoration-content p {
  font-size: 1.2rem;
  color: #4b5563;
  line-height: 1.6;
}

/* 装饰圆形背景 */
.decoration-card::before {
  content: "";
  position: absolute;
  width: 250px;
  height: 250px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3));
  top: -50px;
  right: -50px;
  z-index: 1;
}

.decoration-card::after {
  content: "";
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
  bottom: -30px;
  left: -30px;
  z-index: 1;
}

/* 输入框动画持续时间 */
input {
  transition: all 0.2s ease-out !important;
}

/* 按钮动画效果 */
button {
  transition: all 0.2s ease-out !important;
}

button:active:not(:disabled) {
  transform: scale(0.98);
}

/* 媒体查询 - 桌面端布局 */
@media (min-width: 1024px) {
  .auth-container {
    padding: 2rem;
  }
  
  .auth-content-wrapper {
    flex-direction: row;
    justify-content: center;
    align-items: center;
    gap: 4rem;
  }
  
  .auth-decoration {
    display: flex;
    align-items: center;
  }
  
  .auth-card {
    margin: 0;
    box-shadow: 
      0 8px 30px rgba(0, 0, 0, 0.06),
      0 12px 40px rgba(0, 0, 0, 0.06);
  }
}

/* 平板设备 */
@media (min-width: 768px) and (max-width: 1023px) {
  .auth-card {
    max-width: 480px;
    padding: 0;
  }
  
  .card-content {
    padding: 1.5rem 3rem 3rem;
  }
  
  .auth-container {
    padding: 2rem;
  }
}

/* 小型笔记本和平板横屏 */
@media (min-width: 1024px) and (max-width: 1279px) {
  .decoration-card {
    width: 360px;
    height: 440px;
  }
  
  .auth-content-wrapper {
    gap: 3rem;
  }
}

/* 大型显示器 */
@media (min-width: 1280px) {
  .auth-content-wrapper {
    gap: 5rem;
  }
  
  .decoration-card {
    width: 450px;
    height: 520px;
  }
  
  .decoration-content h2 {
    font-size: 3rem;
  }
  
  .decoration-content p {
    font-size: 1.3rem;
  }
}
</style> 