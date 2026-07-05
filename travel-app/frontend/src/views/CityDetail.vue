<template>
  <div class="page city-detail-page">
    <van-nav-bar
      :title="cityName"
      left-arrow
      @click-left="router.back()"
    />

    <van-loading v-if="loading" type="spinner" class="loading" />

    <template v-else-if="plan">
      <!-- 封面图 + 天气英雄区 -->
      <div class="hero">
        <img v-if="plan.city?.cover_img" :src="plan.city.cover_img" class="hero-img" />
        <div class="hero-overlay"></div>
        <div class="hero-content">
          <h1 class="hero-title">{{ cityName }}</h1>
          <div v-if="weather && weather.icon !== 'N/A'" class="hero-weather">
            <span class="weather-emoji">{{ weatherEmoji(weather.icon) }}</span>
            <span class="weather-temp">{{ weather.temp }}°C</span>
            <span class="weather-desc">{{ weather.weather }}</span>
            <span class="divider">|</span>
            <span>{{ weather.wind }}</span>
            <span class="divider">|</span>
            <span>💧 {{ weather.humidity }}%</span>
          </div>
          <div v-else-if="weather" class="hero-weather weather-na">
            🌤️ 天气数据暂不可用
          </div>
        </div>
      </div>

      <!-- 日期切换 -->
      <van-tabs v-model:active="activeDay" sticky offset-top="46" color="#ff6900" title-active-color="#ff6900">
        <van-tab
          v-for="(dayPlan, idx) in plan.plans"
          :key="idx"
          :title="`第 ${dayPlan.day} 天`"
          :name="idx"
        />
      </van-tabs>

      <!-- 当日路书 -->
      <div class="day-plan" v-if="currentDayPlan">
        <div class="day-title">{{ currentDayPlan.title }}</div>
        <div class="day-tips">
          <van-icon name="info-o" />
          <span>{{ currentDayPlan.tips }}</span>
        </div>

        <div class="timeline">
          <div
            v-for="(spot, sIdx) in currentDayPlan.spots"
            :key="spot.name + sIdx"
            class="timeline-item fade-in-up"
            :style="{ animationDelay: `${sIdx * 0.08}s` }"
          >
            <div class="timeline-time">{{ spot.time }}</div>
            <div class="timeline-dot" :style="{ background: spotColor(spot.name) }"></div>
            <div class="timeline-content">
              <div class="spot-card">
                <div class="spot-icon" :style="{ background: spotColor(spot.name) + '18' }">
                  {{ spotIcon(spot) }}
                </div>
                <div class="spot-info">
                  <div class="spot-header">
                    <span class="spot-name">{{ spot.name }}</span>
                    <span class="spot-duration">{{ spot.duration }}</span>
                  </div>
                  <div class="spot-tip">
                    <van-icon name="location-o" />
                    <span>{{ spot.tip }}</span>
                  </div>
                  <div class="spot-actions">
                    <van-button
                      size="mini"
                      plain
                      type="primary"
                      round
                      icon="location-o"
                      @click="showOnMap(spot)"
                    >地图</van-button>
                    <van-button
                      v-if="sIdx > 0"
                      size="mini"
                      plain
                      round
                      @click="moveUp(sIdx)"
                    >↑ 上移</van-button>
                    <van-button
                      v-if="sIdx < currentDayPlan.spots.length - 1"
                      size="mini"
                      plain
                      round
                      @click="moveDown(sIdx)"
                    >↓ 下移</van-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 地图弹层 -->
      <van-popup
        v-model:show="mapVisible"
        position="bottom"
        :style="{ height: '65%' }"
        round
      >
        <div class="map-popup">
          <div class="map-header">
            <span class="map-title">📍 {{ mapSpot?.name || '景点地图' }}</span>
            <van-icon name="cross" size="20" color="#969799" @click="mapVisible = false" />
          </div>
          <div class="map-body">
            <div class="map-info-card">
              <div class="info-row">
                <span class="info-label">⏰ 时间</span>
                <span class="info-value">{{ mapSpot?.time }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">⌛ 时长</span>
                <span class="info-value">{{ mapSpot?.duration }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">💡 提示</span>
                <span class="info-value">{{ mapSpot?.tip }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">🌐 坐标</span>
                <span class="info-value mono">{{ mapSpot?.lat?.toFixed(4) }}, {{ mapSpot?.lng?.toFixed(4) }}</span>
              </div>
            </div>
            <div class="map-placeholder">
              <div class="map-pin">📍</div>
              <p class="map-spot-name">{{ mapSpot?.name }}</p>
              <p class="map-hint">高德地图 JS API 接入后显示实时地图</p>
            </div>
          </div>
        </div>
      </van-popup>

      <!-- 草稿提示 -->
      <div v-if="tripStore.dirty" class="dirty-tip">
        <div class="dirty-inner">
          <van-icon name="warning-o" />
          <span>行程已调整，未同步云端</span>
          <van-button size="mini" type="primary" round @click="resetDraft">恢复默认</van-button>
        </div>
      </div>
    </template>

    <!-- No plan - offer AI generation -->
    <div v-else class="no-plan">
      <div class="no-plan-icon">🗺️</div>
      <h3 class="no-plan-title">{{ cityName }} 暂无路书</h3>
      <p class="no-plan-desc">让 AI 为你智能生成专属行程</p>
      <van-button type="primary" round @click="goAiPlan">AI 生成行程</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { useTripStore } from '@/stores/trip'

const route = useRoute()
const router = useRouter()
const tripStore = useTripStore()

const cityName = ref(route.params.id || '')
const loading = ref(false)
const plan = ref(null)
const weather = ref(null)
const activeDay = ref(0)
const mapVisible = ref(false)
const mapSpot = ref(null)

const WEATHER_EMOJI = {
  '100': '☀️', '101': '⛅', '104': '☁️', '300': '🌦️', '302': '⛈️',
  '305': '🌦️', '306': '🌧️', '307': '🌧️', '400': '🌨️', '401': '❄️',
  '500': '🌫️', '501': '🌫️',
}
function weatherEmoji(icon) { return WEATHER_EMOJI[icon] || '🌤️' }

// 景点类型 → 颜色 + 图标（基于名称关键词匹配）
const SPOT_PATTERNS = [
  { match: /(故宫|博物馆|文化|遗址|历史|皇城|园林|寺庙|塔|城墙|陵)/, color: '#9b59b6', icon: '🏛️' },
  { match: /(美食|小吃|餐厅|饭馆|烤鸭|火锅|餐|街|夜市|吧)/, color: '#e67e22', icon: '🍜' },
  { match: /(公园|湖|山|景区|自然|森林|海|滩|瀑布|峡谷|竹)/, color: '#27ae60', icon: '🌿' },
  { match: /(乐园|游乐|动物园|海洋|馆|迪斯尼|迪士尼|欢乐)/, color: '#e74c3c', icon: '🎢' },
  { match: /(购物|商场|中心|广场|街|商圈|市场)/, color: '#f39c12', icon: '🛍️' },
]

function classifySpot(name) {
  for (const p of SPOT_PATTERNS) {
    if (p.match.test(name)) return p
  }
  return { match: null, color: '#3498db', icon: '📍' }
}

function spotColor(name) { return classifySpot(name).color }
function spotIcon(spot) {
  // 优先用 activity 字段判断
  if (spot.activity) {
    if (/(吃|饭|餐|美食|火锅|小吃)/.test(spot.activity)) return '🍜'
    if (/(玩|乐|游乐|体验)/.test(spot.activity)) return '🎯'
    if (/(看|观|赏|游)/.test(spot.activity)) return '👀'
  }
  return classifySpot(spot.name).icon
}

const currentDayPlan = computed(() => plan.value?.plans?.[activeDay.value])

async function loadData() {
  loading.value = true
  try {
    await tripStore.loadCityData(cityName.value)
    plan.value = tripStore.currentPlan
    weather.value = tripStore.currentWeather
  } catch (e) {
    // Plan not found - show city info without plan
    plan.value = { city: { name: cityName.value }, plans: null }
  } finally {
    loading.value = false
  }
}

function showOnMap(spot) {
  mapSpot.value = spot
  mapVisible.value = true
}

function moveUp(idx) {
  tripStore.reorderSpots(activeDay.value, idx, idx - 1)
  showToast('已上移')
}
function moveDown(idx) {
  tripStore.reorderSpots(activeDay.value, idx, idx + 1)
  showToast('已下移')
}

function resetDraft() {
  showConfirmDialog({
    title: '恢复原始路书',
    message: '将丢弃当前城市的所有本地调整，确定吗？',
  }).then(() => {
    tripStore.resetLocal(cityName.value)
    loadData()
    showToast('已恢复')
  }).catch(() => {})
}

function goAiPlan() {
  router.push({ path: '/ai/plan', query: { city: cityName.value } })
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    cityName.value = newId
    activeDay.value = 0
    loadData()
  }
})

loadData()
</script>

<style scoped>
.city-detail-page { padding-bottom: 80px; background: var(--bg-page); min-height: 100vh; }

.loading { display: flex; justify-content: center; padding: 60px; }

/* ===== 英雄区 ===== */
.hero {
  position: relative;
  height: 220px;
  overflow: hidden;
}
.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.1) 60%, transparent 100%);
}
.hero-content {
  position: absolute;
  bottom: 20px;
  left: 18px;
  right: 18px;
  color: #fff;
}
.hero-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.hero-weather {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(6px);
  border-radius: 12px;
  padding: 6px 14px;
  display: inline-flex;
  border: 1px solid rgba(255,255,255,0.1);
}
.weather-emoji { font-size: 18px; }
.weather-temp { font-weight: 700; font-size: 16px; }
.weather-desc { opacity: 0.9; }
.divider { opacity: 0.4; }
.weather-na { font-size: 13px; opacity: 0.8; backdrop-filter: none; background: rgba(0,0,0,0.25); }

/* ===== 路书内容 ===== */
.day-plan { padding: 14px; }

.day-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.day-tips {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: linear-gradient(135deg, #fff8e6, #fff3d6);
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 15px;
  color: #d48806;
  margin-bottom: 20px;
  border-left: 3px solid #faab0c;
}

/* ===== 时间轴 ===== */
.timeline {
  position: relative;
  padding-left: 4px;
}

.timeline-item {
  position: relative;
  padding-left: 85px;
  padding-bottom: 20px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 75px;
  top: 28px;
  bottom: 0;
  width: 2.5px;
  background: linear-gradient(to bottom, var(--primary-light), var(--border));
  border-radius: 2px;
}

.timeline-item:last-child::before { display: none; }

.timeline-time {
  position: absolute;
  left: 0;
  top: 6px;
  width: 68px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-hint);
  text-align: right;
  background: var(--bg-page);
  padding: 2px 8px;
  border-radius: 6px;
}

.timeline-dot {
  position: absolute;
  left: 68px;
  top: 8px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--mi-orange);
  border: 3px solid #fff;
  box-shadow: 0 0 0 2px var(--mi-orange), 0 2px 6px rgba(0,0,0,0.1);
  z-index: 1;
  transition: transform 0.2s;
}
.timeline-item:hover .timeline-dot {
  transform: scale(1.2);
}

/* ===== 景点卡片 ===== */
.spot-card {
  display: flex;
  gap: 12px;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  animation: fadeInUp 0.4s ease both;
}
.spot-card:hover {
  transform: translateX(3px);
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.spot-card:active {
  transform: scale(0.98);
}

.spot-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.spot-info { flex: 1; min-width: 0; }

.spot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.spot-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.spot-duration {
  font-size: 13px;
  font-weight: 600;
  color: var(--mi-orange);
  background: var(--mi-orange) + '0f';
  padding: 2px 8px;
  border-radius: 8px;
  white-space: nowrap;
}

.spot-tip {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 14px;
  color: var(--text-hint);
  margin-bottom: 10px;
  line-height: 1.4;
}

.spot-actions {
  display: flex;
  gap: 6px;
}

/* ===== 地图弹层 ===== */
.map-popup { height: 100%; display: flex; flex-direction: column; }
.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}
.map-title { font-size: 18px; font-weight: 600; }
.map-body { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }

.map-info-card {
  padding: 14px 18px;
  background: #f8f9fd;
  margin: 8px 12px;
  border-radius: 12px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 15px; color: var(--text-hint); }
.info-value { font-size: 15px; font-weight: 500; color: var(--text-primary); }
.mono { font-family: 'SF Mono', 'Fira Code', monospace; letter-spacing: 0.5px; }

.map-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  color: var(--text-hint);
  gap: 8px;
  margin: 12px;
  border-radius: 14px;
}
.map-pin { font-size: 56px; animation: float 2.5s ease-in-out infinite; }
.map-spot-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.map-hint { font-size: 14px; color: var(--text-hint); }

/* ===== 草稿提示条 ===== */
.dirty-tip {
  position: fixed;
  bottom: 16px;
  left: 16px;
  right: 16px;
  z-index: 100;
  animation: slideUp 0.3s ease;
}
.dirty-inner {
  background: #fffbe8;
  border: 1px solid #ffe58f;
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #d48806;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.dirty-inner > span { flex: 1; }

/* No plan */
.no-plan {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}
.no-plan-icon { font-size: 64px; margin-bottom: 16px; }
.no-plan-title { font-size: 20px; font-weight: 700; margin: 0 0 8px; }
.no-plan-desc { font-size: 14px; color: var(--text-hint); margin: 0 0 24px; }
</style>
