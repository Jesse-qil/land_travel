import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as citiesApi from '@/api/cities'

const STORAGE_KEY = 'travel_trips'

function loadLocalTrips() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

export const useTripStore = defineStore('trip', () => {
  const currentPlan = ref(null)
  const currentCity = ref(null)
  const currentWeather = ref(null)
  const dirty = ref(false)
  const localVersion = ref(0)
  const serverVersion = ref(0)
  const localTrips = ref(loadLocalTrips())

  const planDays = computed(() => currentPlan.value?.plans?.length || 0)

  async function loadCityData(city) {
    const [planRes, weatherRes] = await Promise.all([
      citiesApi.fetchPlan(city),
      citiesApi.fetchWeather(city).catch(() => null),
    ])
    currentPlan.value = planRes.data
    currentCity.value = planRes.data?.city || null
    currentWeather.value = weatherRes?.data || null
    // 合并本地草稿
    const local = localTrips.value[city]
    if (local) {
      currentPlan.value = local
    }
    return planRes.data
  }

  function reorderSpots(dayIndex, fromIndex, toIndex) {
    if (!currentPlan.value?.plans?.[dayIndex]) return
    const spots = currentPlan.value.plans[dayIndex].spots
    const [moved] = spots.splice(fromIndex, 1)
    spots.splice(toIndex, 0, moved)
    markDirty()
  }

  function markDirty() {
    dirty.value = true
    if (currentCity.value) {
      localTrips.value[currentCity.value.name] = currentPlan.value
      localStorage.setItem(STORAGE_KEY, JSON.stringify(localTrips.value))
    }
  }

  function resetLocal(cityName) {
    delete localTrips.value[cityName]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(localTrips.value))
    dirty.value = false
  }

  return {
    currentPlan,
    currentCity,
    currentWeather,
    dirty,
    localVersion,
    serverVersion,
    localTrips,
    planDays,
    loadCityData,
    reorderSpots,
    markDirty,
    resetLocal,
  }
})
