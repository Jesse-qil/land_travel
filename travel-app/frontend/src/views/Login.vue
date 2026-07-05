<template>
  <div class="login-page">
    <van-nav-bar title="登录" />

    <div class="login-header">
      <div class="logo">🏔️</div>
      <h1 class="title">陆地旅行智能推荐</h1>
      <p class="subtitle">基于实时数据的智能旅行路书</p>
    </div>

    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="登录" name="login">
        <van-form @submit="onLogin" class="form">
          <van-cell-group inset>
            <van-field
              v-model="loginForm.email"
              name="email"
              label="邮箱"
              placeholder="请输入邮箱"
              :rules="[{ required: true, message: '请输入邮箱' }, { pattern: emailPattern, message: '邮箱格式不正确' }]"
            />
            <van-field
              v-model="loginForm.password"
              type="password"
              name="password"
              label="密码"
              placeholder="请输入密码"
              :rules="[{ required: true, message: '请输入密码' }]"
            />
          </van-cell-group>
          <div class="submit-wrap">
            <van-button block round type="primary" native-type="submit" :loading="loading">
              登录
            </van-button>
          </div>
        </van-form>
      </van-tab>

      <van-tab title="注册" name="register">
        <van-form @submit="onRegister" class="form">
          <van-cell-group inset>
            <van-field
              v-model="registerForm.nickname"
              name="nickname"
              label="昵称"
              placeholder="请输入昵称"
              :rules="[{ required: true, message: '请输入昵称' }]"
            />
            <van-field
              v-model="registerForm.email"
              name="email"
              label="邮箱"
              placeholder="请输入邮箱"
              :rules="[{ required: true, message: '请输入邮箱' }, { pattern: emailPattern, message: '邮箱格式不正确' }]"
            />
            <van-field
              v-model="registerForm.password"
              type="password"
              name="password"
              label="密码"
              placeholder="6-64 位"
              :rules="[{ required: true, message: '请输入密码' }, { pattern: /^.{6,64}$/, message: '密码 6-64 位' }]"
            />
          </van-cell-group>
          <div class="submit-wrap">
            <van-button block round type="primary" native-type="submit" :loading="loading">
              注册
            </van-button>
          </div>
        </van-form>
      </van-tab>
    </van-tabs>

    <div class="guest-entry">
      <van-button plain hairline type="primary" size="small" @click="continueAsGuest">
        以游客身份继续浏览
      </van-button>
    </div>

    <div class="tips">
      <van-icon name="info-o" />
      <span>已有账号请登录，新用户请先注册</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const emailPattern = /^[\w.+-]+@[\w-]+\.[\w.-]+$/

const loginForm = reactive({ email: '', password: '' })
const registerForm = reactive({ nickname: '', email: '', password: '' })

async function onLogin() {
  loading.value = true
  try {
    await userStore.login(loginForm.email, loginForm.password)
    showSuccessToast('登录成功')
    redirectAfterAuth()
  } catch (e) {
    showFailToast(e?.message || '登录失败')
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  loading.value = true
  try {
    await userStore.register(registerForm.email, registerForm.password, registerForm.nickname)
    showSuccessToast('注册成功')
    redirectAfterAuth()
  } catch (e) {
    showFailToast(e?.message || '注册失败')
  } finally {
    loading.value = false
  }
}

function continueAsGuest() {
  redirectAfterAuth()
}

function redirectAfterAuth() {
  const redirect = route.query.redirect || '/home'
  router.replace(redirect)
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.login-header {
  text-align: center;
  padding: 40px 20px 24px;
  background: linear-gradient(135deg, #ff6900 0%, #e55d00 100%);
  color: #fff;
}

.logo {
  font-size: 56px;
  line-height: 1;
}

.title {
  margin-top: 12px;
  font-size: 22px;
  font-weight: 600;
}

.subtitle {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.85;
}

.form {
  margin-top: 20px;
}

.submit-wrap {
  padding: 20px;
}

.guest-entry {
  text-align: center;
  margin: 8px 0 16px;
}

.tips {
  text-align: center;
  font-size: 12px;
  color: #969799;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
</style>
