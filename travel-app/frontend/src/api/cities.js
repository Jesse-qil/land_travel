import client from './client'

/** 城市列表 */
export function fetchCities(params = {}) {
  return client.get('/cities', { params })
}

/** 标准化路书 */
export function fetchPlan(city) {
  return client.get(`/plans/${city}`)
}

/** 实时天气 */
export function fetchWeather(city) {
  return client.get(`/weather/${city}`)
}
