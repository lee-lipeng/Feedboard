import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import FeedManageView from '../views/FeedManageView.vue';
import ReadLaterView from '../views/ReadLaterView.vue';
import FavoritesView from '../views/FavoritesView.vue';
import SettingsView from '../views/SettingsView.vue';
import ProfileView from '../views/ProfileView.vue';
import LatestView from '../views/LatestView.vue';
import UnreadView from '../views/UnreadView.vue';
import SearchView from '@/views/SearchView.vue';
import ArticleView from '@/views/ArticleView.vue';

// 身份验证守卫
import { useAuthStore } from '@/stores/auth';
import { useArticleStore } from '@/stores/article';

const requireAuth = (to: any, from: any, next: any) => {
  const authStore = useAuthStore();
  if (!authStore.isAuthenticated) {
    next({ name: 'login' });
  } else {
    next();
  }
};

// 路由切换前清理数据
const cleanupArticleData = (to: any, from: any, next: any) => {
  // 当路由发生变化时,重置文章列表数据
  // 这样可以避免在页面切换时显示上一个页面的数据
  const articleStore = useArticleStore();
  articleStore.resetArticles();
  next();
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/feedboard/'),
  routes: [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    beforeEnter: [requireAuth, cleanupArticleData]
  },
  {
    path: '/feeds/:feedId',
    name: 'feed-detail',
    component: () => import('../views/FeedDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/latest',
    name: 'latest',
    component: LatestView,
    beforeEnter: [requireAuth, cleanupArticleData]
  },
  {
    path: '/unread',
    name: 'unread',
    component: UnreadView,
    beforeEnter: [requireAuth, cleanupArticleData]
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
    },
    {
      path: '/feeds',
      name: 'feeds',
      component: FeedManageView,
      beforeEnter: requireAuth
  },
  {
      path: '/read-later',
      name: 'read-later',
      component: ReadLaterView,
      beforeEnter: [requireAuth, cleanupArticleData]
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: FavoritesView,
    beforeEnter: [requireAuth, cleanupArticleData]
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    beforeEnter: requireAuth
  },
  {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      beforeEnter: requireAuth
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
    meta: { requiresAuth: true }
  },
  {
    path: '/articles/:articleId',
    name: 'article-detail',
    component: ArticleView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: HomeView // 或者一个专门的404页面
  }
  ],
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置且不是文章详情页面，则使用保存的位置
    if (savedPosition && !to.hash.includes('article')) {
      return savedPosition;
    } else {
      return { top: 0, behavior: 'auto' };
    }
  },
});

export default router;
 