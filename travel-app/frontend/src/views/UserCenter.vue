<template>
  <div class="page">
    <van-nav-bar title="我的" />
    <div class="user-card">
      <template v-if="userStore.isLoggedIn">
        <van-cell title="昵称" :value="userStore.user?.nickname || 'N/A'" />
        <van-cell title="邮箱" :value="userStore.user?.email || 'N/A'" />
        <div class="logout-wrap">
          <van-button block type="danger" @click="onLogout">退出登录</van-button>
        </div>
      </template>
      <template v-else>
        <div class="guest-block">
          <van-icon name="user-o" size="48" />
          <p class="guest-title">游客身份</p>
          <p class="guest-desc">登录后可同步行程、收藏、评论</p>
          <van-button type="primary" round @click="goLogin">前往登录</van-button>
          <p class="guest-tip">邮箱登录尚未配置，可先以游客身份浏览</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
const router = useRouter()
const userStore = useUserStore()
function onLogout() {
  userStore.logout()
  router.replace('/home')
}
function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.user-card { margin: 12px; }
.logout-wrap { padding: 20px; }
.guest-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 40px 20px;
  background: #fff;
  border-radius: 12px;
  margin: 12px;
}
.guest-title { font-size: 18px; font-weight: 600; margin: 0; }
.guest-desc { font-size: 13px; color: #969799; margin: 0 0 12px; }
.guest-tip { font-size: 12px; color: #c8c9cc; margin: 12px 0 0; }
</style>
