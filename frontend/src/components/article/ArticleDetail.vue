<template>
  <div class="article-detail">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="article-loading">
      <div class="loading-spinner"></div>
      <p>加载文章中...</p>
    </div>
    
    <!-- 文章不存在 -->
    <div v-else-if="!article" class="article-not-found">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      </div>
      <h2>文章不存在或已被删除</h2>
      <button class="back-button" @click="$emit('back')">返回列表</button>
    </div>
    
    <!-- 文章详情 -->
    <div v-else class="article-container">
      <!-- 文章头部 -->
      <div class="article-header">
        <h1 class="article-title">{{ article.title }}</h1>
        
        <div class="article-meta">
          <div class="meta-primary">
            <span class="article-source">{{ article.feed_title }}</span>
            <span v-if="article.author" class="article-author">{{ article.author }}</span>
            <span v-if="article.published_at" class="article-date">{{ formatDate(article.published_at) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 文章内容 -->
      <div class="article-content" ref="articleContentRef">
        <!-- 主图 -->
        <div v-if="article.image_url" class="article-image-container">
          <img :src="article.image_url" :alt="article.title" class="article-image" @error="handleImageError" />
        </div>
        
        <!-- 正文内容 -->
        <div v-if="article.content" class="article-body" v-html="sanitizeContent(article.content)"></div>
        
        <!-- 摘要内容 -->
        <div v-else-if="article.summary" class="article-summary" v-html="sanitizeContent(article.summary)"></div>
        
        <!-- 无内容 -->
        <div v-else class="article-no-content">
          <p>该文章无可读内容，请点击"原文链接"查看原文。</p>
        </div>
        
        <!-- 原文链接 -->
        <div class="article-footer">
          <a 
            :href="article.url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="original-link"
          >
            阅读原文
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="link-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
          </a>
        </div>
      </div>
      
      <!-- 固定在右侧的操作按钮 -->
      <div class="fixed-action-buttons">
        <button 
          class="fixed-action-button" 
          :class="{ 'active': article.is_favorite }"
          @click="toggleFavorite"
          :title="article.is_favorite ? '取消收藏' : '添加到收藏'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="fixed-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
          </svg>
          <div class="button-text">
            <span>收</span>
            <span>藏</span>
          </div>
        </button>
        
        <button 
          class="fixed-action-button"
          :class="{ 'active': article.read_later }"
          @click="toggleReadLater"
          :title="article.read_later ? '从稍后阅读中移除' : '添加到稍后阅读'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="fixed-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
          </svg>
          <div class="button-text">
            <span>稍</span>
            <span>后</span>
            <span>阅</span>
            <span>读</span>
          </div>
        </button>
        
        <a 
          :href="article.url" 
          target="_blank" 
          rel="noopener noreferrer"
          class="fixed-action-button"
          title="在新标签页中打开原文"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="fixed-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
          <div class="button-text">
            <span>原</span>
            <span>文</span>
          </div>
        </a>
        
        <button class="fixed-action-button" @click="$emit('back')" title="返回文章列表">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="fixed-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
          </svg>
          <div class="button-text">
            <span>返</span>
            <span>回</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useArticleStore, type Article } from '@/stores/article';
import { useRoute } from 'vue-router';
import notification from '@/utils/notification';
import DOMPurify from 'dompurify';

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  },
  article: {
    type: Object as () => Article | null,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update', 'back']);

const articleStore = useArticleStore();
const articleContentRef = ref<HTMLElement | null>(null);
const route = useRoute();

// 滚动完成标记，确保初始滚动只执行一次
const initialScrollDone = ref(false);

// 判断当前是否在收藏或稍后阅读页面
const isFromSavedPages = computed(() => {
  console.log('当前路径:', route.path);
  return route.path.includes('/favorites') || route.path.includes('/readlater');
});

// 切换收藏状态
async function toggleFavorite() {
  if (!props.article) return;
  
  try {
    // 获取当前阅读位置并转换为整数
    const currentPosition = getScrollPosition();
    const newStatus = !props.article.is_favorite;
    
    // 先在本地更新状态,避免闪烁
    const updatedArticle = { ...props.article, is_favorite: newStatus };
    
    // 预先发送通知
    if (newStatus) {
      notification.success('已添加到收藏');
    } else {
      notification.success('已取消收藏');
    }
    
    // 更新服务器状态
    const result = await articleStore.updateArticleStatus(props.article.id, { 
      is_favorite: newStatus,
      read_position: currentPosition
    });
    
    if (result) {
      emit('update', props.article.id);
      
      // 触发自定义事件,通知更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } catch (error) {
    console.error('更新收藏状态失败:', error);
    notification.error('操作失败，请稍后重试');
  }
}

// 切换稍后阅读状态
async function toggleReadLater() {
  if (!props.article) return;
  
  try {
    // 获取当前阅读位置并转换为整数
    const currentPosition = getScrollPosition();
    const newStatus = !props.article.read_later;
    
    // 先在本地更新状态,避免闪烁
    const updatedArticle = { ...props.article, read_later: newStatus };
    
    // 预先发送通知
    if (newStatus) {
      notification.success('已添加到稍后阅读');
    } else {
      notification.success('已从稍后阅读中移除');
    }
    
    // 更新服务器状态
    const result = await articleStore.updateArticleStatus(props.article.id, { 
      read_later: newStatus,
      read_position: currentPosition
    });
    
    if (result) {
      emit('update', props.article.id);
      
      // 触发自定义事件,通知更新徽章计数
      document.dispatchEvent(new CustomEvent('update-badge-counts'));
    }
  } catch (error) {
    console.error('更新稍后阅读状态失败:', error);
    notification.error('操作失败，请稍后重试');
  }
}

// 格式化日期
function formatDate(dateString: string | null): string {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 内容安全处理
function sanitizeContent(content: string): string {
  // 使用DOMPurify净化HTML，防止XSS攻击
  return DOMPurify.sanitize(content, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img', 'ul', 'ol', 'li',
      'blockquote', 'code', 'pre', 'div', 'span', 'br', 'strong', 'em', 'b', 'i',
      'figure', 'figcaption', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ],
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'class', 'target', 'rel'
    ]
  });
}

// 处理图片加载错误
function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
}

// 辅助函数：获取可滚动的容器元素
function getScrollableElement(): HTMLElement | null {
  return document.querySelector('.page-content');
}

// 辅助函数：获取当前滚动位置
function getScrollPosition(): number {
  const el = getScrollableElement();
  return el ? Math.round(el.scrollTop) : 0;
}

// 唯一的入口函数，结合了防重入和滚动逻辑
function performInitialScroll() {
  // 如果初始滚动已经完成，则直接退出，不再执行任何操作
  if (initialScrollDone.value) {
    return;
  }
  
  const scrollableElement = getScrollableElement();
  if (!scrollableElement) return;

  // 使用轮询检查内容是否加载完毕
  let attempts = 0;
  const intervalId = setInterval(() => {
    attempts++;
    // 如果5秒后内容高度仍不满足或无法滚动，则超时并强制滚动
    if (attempts > 50) {
      clearInterval(intervalId);
      console.warn('滚动检查超时，执行最终滚动尝试。');
      scrollToSavedPosition();
      initialScrollDone.value = true; // 标记为完成
      return;
    }

    // 检查内容高度是否已足够支持滚动
    const targetHeight = (props.article?.read_position && isFromSavedPages.value) ? props.article.read_position : 50;
    if (scrollableElement.scrollHeight > targetHeight) {
      clearInterval(intervalId);
      console.log(`内容已加载，执行平滑滚动 (尝试次数: ${attempts})。`);
      scrollToSavedPosition();
      initialScrollDone.value = true; // 标记为完成
    }
  }, 100);
}

// 滚动到保存的阅读位置
function scrollToSavedPosition() {
  const scrollableElement = getScrollableElement();

  if (
    scrollableElement &&
    isFromSavedPages.value &&
    props.article &&
    props.article.read_position &&
    props.article.read_position > 0
  ) {
    const targetPosition = Math.round(props.article.read_position);
    console.log(`准备平滑滚动到阅读位置: ${targetPosition}`);

    // 使用动画滚动
    scrollableElement.scrollTo({
      top: targetPosition,
      behavior: 'smooth'
    });
  } else if (scrollableElement) {
    // 其他情况滚动到顶部（同样使用平滑动画）
    scrollableElement.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
}

// 保存当前阅读位置，使用节流函数避免频繁调用API
const saveReadPosition = (() => {
  let lastSavedPosition = 0;
  let saveTimer: number | null = null;
  let lastSaveTime = 0;
  
  return function() {
    if (isFromSavedPages.value && props.article) {
      const currentPosition = getScrollPosition();
      const now = Date.now();
      
      // 如果位置变化超过100px或者距离上次保存超过5秒，才保存
      if ((Math.abs(currentPosition - lastSavedPosition) > 100 || now - lastSaveTime > 5000) && currentPosition > 0) {
        // 清除之前的定时器
        if (saveTimer !== null) {
          clearTimeout(saveTimer);
        }
        
        // 设置新的定时器，延迟2秒保存
        saveTimer = setTimeout(() => {
          console.log('保存阅读位置:', currentPosition);
          articleStore.updateArticleStatus(props.article!.id, { 
            read_position: currentPosition
          });
          
          // 更新上次保存的位置和时间
          lastSavedPosition = currentPosition;
          lastSaveTime = Date.now();
          saveTimer = null;
        }, 2000) as unknown as number;
      }
    }
  };
})();

// --- 生命周期钩子 ---
let scrollTimer: number | null = null;
const handleScroll = () => {
  if (scrollTimer !== null) {
    clearTimeout(scrollTimer);
  }
  scrollTimer = setTimeout(saveReadPosition, 500) as unknown as number;
};

onMounted(() => {
  // 核心修正：使用"先声明，后赋值"的模式来创建一次性侦听器
  let unwatch: (() => void) | null = null;

  const watcherCallback = (newArticle: Article | null) => {
    if (newArticle) {
      // 步骤 1：调用唯一的滚动入口函数
      performInitialScroll();

      // 步骤 2：如果文章未读，则标记为已读（这也是初始加载的一部分）
      if (!newArticle.is_read) {
        articleStore.updateArticleStatus(newArticle.id, { is_read: true })
          .then(() => {
            emit('update'); // 通知父组件更新状态
          })
          .catch(error => {
            console.error('标记已读失败:', error);
          });
      }
      
      // 步骤 3：完成所有初始加载任务后，立即销毁侦听器
      if (unwatch) {
        unwatch();
      }
    }
  };
  
  // 将 watch 返回的销毁函数赋值给之前声明的变量
  unwatch = watch(() => props.article, watcherCallback, { immediate: true });

  // 将滚动事件监听器添加到正确的容器
  const scrollableElement = getScrollableElement();
  if (scrollableElement) {
    scrollableElement.addEventListener('scroll', handleScroll);
  }
});

onUnmounted(() => {
  // 组件销毁时清理
  const scrollableElement = getScrollableElement();
  if (scrollableElement) {
    scrollableElement.removeEventListener('scroll', handleScroll);
  }
  if (scrollTimer !== null) {
    clearTimeout(scrollTimer);
  }
  // 退出前最后保存一次位置
  saveReadPosition();
});
</script>

<style scoped>
.article-detail {
  width: 100%;
  max-width: 100%;
  animation: fade-in 0.3s ease-in-out;
  position: relative; /* 确保定位正确 */
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 加载状态 */
.article-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  min-height: 300px; /* 确保有足够的高度 */
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 文章不存在 */
.article-not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  text-align: center;
}

.error-icon {
  width: 4rem;
  height: 4rem;
  color: #ef4444;
  margin-bottom: 1.5rem;
}

.article-not-found h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.back-button {
  padding: 0.75rem 1.5rem;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: #4f46e5;
}

/* 文章容器 */
.article-container {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* 文章头部 */
.article-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.article-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.meta-primary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.article-source {
  color: #6366f1;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  background-color: #ede9fe;
  border-radius: 0.25rem;
}

.article-author {
  color: #4b5563;
}

.article-date {
  color: #6b7280;
}

/* 文章内容 */
.article-content {
  padding: 1.5rem;
}

.article-image-container {
  margin-bottom: 1.5rem;
  overflow: hidden;
  border-radius: 0.375rem;
}

.article-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  background-color: #f9fafb;
}

.article-body {
  line-height: 1.8;
  color: #1f2937;
  font-size: 1rem;
}

/* 文章摘要 */
.article-summary {
  line-height: 1.8;
  color: #4b5563;
  font-size: 1rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.375rem;
  font-style: italic;
}

/* 无内容提示 */
.article-no-content {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
  border-radius: 0.375rem;
}

/* 文章底部 */
.article-footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: center;
}

.original-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #6366f1;
  color: white;
  border-radius: 0.375rem;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.original-link:hover {
  background-color: #4f46e5;
}

.link-icon {
  width: 1rem;
  height: 1rem;
}

/* 响应式布局 */
@media (min-width: 768px) {
  .article-meta {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .article-title {
    font-size: 1.75rem;
  }
  
  .article-content {
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .article-title {
    font-size: 2rem;
  }
  
  .article-container {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .article-body,
  .article-summary {
    font-size: 1.125rem;
  }
}

/* 固定在右侧的操作按钮 */
.fixed-action-buttons {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 100;
}

.fixed-action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  padding: 0.5rem;
  background-color: white;
  border: none;
  border-radius: 12px;
  color: #4b5563;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.fixed-action-button:hover {
  background-color: #f9fafb;
  color: #6366f1;
  transform: translateX(-5px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.15);
}

.fixed-action-button.active {
  background-color: #6366f1;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

.fixed-icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-bottom: 0.25rem;
  transition: transform 0.2s ease;
}

.button-text {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.1rem;
  font-size: 0.7rem;
  line-height: 1;
  text-align: center;
}

.fixed-action-button:hover .fixed-icon {
  transform: scale(1.1);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .fixed-action-buttons {
    bottom: 20px;
    top: auto;
    right: 20px;
    transform: none;
    flex-direction: row;
    gap: 0.75rem;
  }
  
  .fixed-action-button {
    width: 46px;
    height: 46px;
    padding: 0.4rem;
    border-radius: 10px;
  }
  
  .fixed-action-button:hover {
    transform: translateY(-5px);
  }
  
  .fixed-icon {
    width: 1.25rem;
    height: 1.25rem;
    margin-bottom: 0.15rem;
  }
  
  .button-text {
    font-size: 0.65rem;
  }
}
</style>

<style>
/* 全局样式，确保页面切换时不会出现定位问题 */
.view-transition {
  position: relative;
  min-height: 100vh;
}

/* 文章内容格式化，注意这里没有scoped */
.article-body h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: #1f2937;
}

.article-body h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: #1f2937;
}

.article-body h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: #1f2937;
}

.article-body h4,
.article-body h5,
.article-body h6 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: #1f2937;
}

.article-body p {
  margin-bottom: 1rem;
}

.article-body img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  border-radius: 0.375rem;
}

.article-body a {
  color: #6366f1;
  text-decoration: none;
}

.article-body a:hover {
  text-decoration: underline;
}

.article-body ul,
.article-body ol {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.article-body li {
  margin-bottom: 0.5rem;
}

.article-body blockquote {
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  border-left: 4px solid #e5e7eb;
  background-color: #f9fafb;
  color: #4b5563;
}

.article-body pre {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #1f2937;
  color: #f9fafb;
  border-radius: 0.375rem;
  overflow-x: auto;
}

.article-body code {
  padding: 0.25rem 0.5rem;
  background-color: #f3f4f6;
  border-radius: 0.25rem;
  font-family: monospace;
}

.article-body pre code {
  padding: 0;
  background-color: transparent;
}

.article-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.article-body th,
.article-body td {
  border: 1px solid #e5e7eb;
  padding: 0.5rem;
}

.article-body th {
  background-color: #f9fafb;
  font-weight: 600;
}

.article-body figure {
  margin: 1.5rem 0;
}

.article-body figcaption {
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style> 