<template>
  <MainLayout>
    <div class="search-view-container">
      <h1 class="search-title">
        搜索结果: <span class="search-query">"{{ query }}"</span>
      </h1>

      <div v-if="isLoading" class="loading-state">
        正在努力搜索中...
      </div>

      <div v-else-if="error" class="error-state">
        <p>搜索时遇到问题：{{ error }}</p>
      </div>
      
      <div v-else-if="articles.length === 0" class="empty-state">
        <p>没有找到与 "{{ query }}" 相关的文章。</p>
        <p>请尝试使用其他关键词。</p>
      </div>

      <div v-else class="results-list">
        <!-- 搜索结果列表 -->
        <router-link
          v-for="article in articles"
          :key="article.id"
          :to="`/articles/${article.id}`"
          class="article-item-link"
        >
          <div class="article-item">
            <h2 class="article-title" v-html="highlight(article.title)"></h2>
            <p class="article-summary" v-html="generateSnippet(article.summary || article.content || '', query)"></p>
            <div class="article-meta">
              <span class="feed-title">{{ article.feed_title }}</span>
              <span class="published-date">{{ formatDate(article.published_at) }}</span>
            </div>
          </div>
        </router-link>
        
        <!-- TODO: Add pagination or infinite scroll -->
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import MainLayout from '@/components/layout/MainLayout.vue';
import { useArticleStore } from '@/stores/article';
import { storeToRefs } from 'pinia';

const route = useRoute();
const articleStore = useArticleStore();

const query = ref(route.query.q as string || '');

const { searchResults: articles, isLoading, error } = storeToRefs(articleStore);

const highlight = (text: string) => {
  if (!query.value || !text) {
    return text;
  }
  const regex = new RegExp(query.value.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'gi');
  return text.replace(regex, (match) => `<mark>${match}</mark>`);
};

const generateSnippet = (text: string, query: string, contextLength = 80) => {
  if (!query || !text) {
    return (text || '').substring(0, contextLength * 2);
  }

  const safeQuery = query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const regex = new RegExp(safeQuery, 'i');
  const match = text.match(regex);

  if (!match || typeof match.index === 'undefined') {
    return highlight(text.substring(0, contextLength * 2) + (text.length > contextLength * 2 ? '...' : ''));
  }

  const matchIndex = match.index;
  const matchLength = match[0].length;
  
  const start = Math.max(0, matchIndex - contextLength);
  const end = Math.min(text.length, matchIndex + matchLength + contextLength);

  let snippet = text.substring(start, end);
  
  if (start > 0) {
    snippet = '... ' + snippet;
  }
  if (end < text.length) {
    snippet = snippet + ' ...';
  }
  
  return highlight(snippet);
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const performSearch = () => {
  if (query.value) {
    articleStore.searchArticles(query.value);
  }
};

watch(() => route.query.q, (newQuery) => {
  query.value = newQuery as string || '';
  performSearch();
}, { immediate: true });

</script>

<style scoped>
.search-view-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.search-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 2rem;
}

.search-query {
  color: var(--primary-color, #6366f1);
}

.article-item-link {
  display: block;
  text-decoration: none;
  color: inherit;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.article-item-link:hover {
  background-color: #f9fafb; /* gray-50 */
}

.article-item {
  padding: 1.5rem;
}

.article-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.article-summary {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.article-meta {
  font-size: 0.875rem;
  color: #6b7280;
  display: flex;
  gap: 1rem;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #6b7280;
}
</style>
<style>
/* Global style for highlighted text */
mark {
  background-color: #fef08a; /* yellow-200 */
  padding: 0.1em 0.2em;
  border-radius: 3px;
}
</style> 