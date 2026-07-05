import axios from 'axios'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

client.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data.code === 0) {
      return data
    }
    // 业务错误
    showToast(data.message || '请求失败')
    return Promise.reject(data)
  },
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      showToast('登录已过期，请重新登录')
      setTimeout(() => {
        window.location.href = '/login'
      }, 1000)
    } else {
      showToast(error.message || '网络异常')
    }
    return Promise.reject(error)
  }
)

export default client
