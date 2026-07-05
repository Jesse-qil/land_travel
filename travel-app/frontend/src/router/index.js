import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', keepAlive: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/city/:id',
    name: 'CityDetail',
    component: () => import('@/views/CityDetail.vue'),
    meta: { title: '城市详情' },
  },
  {
    path: '/ai/plan',
    name: 'AIPlan',
    component: () => import('@/views/AIPlan.vue'),
    meta: { title: 'AI 行程' },
  },
  {
    path: '/ai/ask',
    name: 'AIAsk',
    component: () => import('@/views/AIAsk.vue'),
    meta: { title: 'AI 问答' },
  },
  {
    path: '/user',
    name: 'UserCenter',
    component: () => import('@/views/UserCenter.vue'),
    meta: { title: '我的' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { title: '后台管理', requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 陆地旅行` : '陆地旅行'
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
