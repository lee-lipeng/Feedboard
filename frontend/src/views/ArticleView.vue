<template>
  <MainLayout>
    <div class="article-view-container">
      <ArticleDetail
        v-if="articleId"
        :article-id="articleId"
        :article="currentArticle"
        :is-loading="isLoading"
        @back="goBack"
      />
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MainLayout from '@/components/layout/MainLayout.vue';
import ArticleDetail from '@/components/article/ArticleDetail.vue';
import { useArticleStore } from '@/stores/article';
import { storeToRefs } from 'pinia';

const route = useRoute();
const router = useRouter();
const articleStore = useArticleStore();

const articleId = computed(() => Number(route.params.articleId));

const { currentArticle, isLoading } = storeToRefs(articleStore);

const goBack = () => {
  // 检查是否有历史记录，否则返回首页
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/');
  }
};

watch(
  articleId,
  (newId) => {
    if (newId) {
      articleStore.fetchArticle(newId);
    }
  },
  { immediate: true }
);

</script>

<style scoped>
.article-view-container {
  max-width: 100%;
  margin: 0 auto;
}
</style> 