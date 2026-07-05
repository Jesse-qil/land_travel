import client from './client'

/** 邮箱登录（接入 Supabase 后由后端代理） */
export function login(email, password) {
  return client.post('/auth/login', { email, password })
}

/** 邮箱注册 */
export function register(email, password, nickname) {
  return client.post('/auth/register', { email, password, nickname })
}

/** 游客会话 */
export function getGuestSession() {
  return client.get('/auth/guest')
}

/** 获取当前用户 */
export function fetchMe() {
  return client.get('/auth/me')
}

/** 登出 */
export function logout() {
  return client.post('/auth/logout')
}
