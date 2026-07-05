import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isGuest = computed(() => !isLoggedIn.value)

  function setAuth(tokenValue, userValue) {
    token.value = tokenValue
    user.value = userValue
    localStorage.setItem('token', tokenValue)
    localStorage.setItem('user', JSON.stringify(userValue))
  }

  async function login(email, password) {
    const res = await authApi.login(email, password)
    setAuth(res.data.access_token, res.data.user)
    return res
  }

  async function register(email, password, nickname) {
    const res = await authApi.register(email, password, nickname)
    setAuth(res.data.access_token, res.data.user)
    return res
  }

  function logout() {
    authApi.logout().catch(() => {})
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchMe() {
    const res = await authApi.fetchMe()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    return res
  }

  return {
    token,
    user,
    isLoggedIn,
    isGuest,
    setAuth,
    login,
    register,
    logout,
    fetchMe,
  }
})
