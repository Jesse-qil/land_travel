<template>
  <div class="page mi-home">
    <!-- Xiaomi-style Header -->
    <header class="mi-header">
      <div class="mi-header-inner">
        <div class="mi-logo">
          🏔️ <span>陆地旅行</span>
        </div>
        <nav class="mi-nav">
          <a href="/home" class="active">首页</a>
          <a href="/ai/plan">AI行程</a>
          <a href="/ai/ask">问答</a>
          <a href="/user">我的</a>
        </nav>
        <div class="mi-nav-right">
          <div class="mi-search-box">
            <van-icon name="search" size="14" color="#999" />
            <input v-model="keyword" placeholder="搜索城市" @keyup.enter="onSearch" />
          </div>
          <router-link to="/login" class="mi-login-btn" v-if="!userStore.isLoggedIn">
            <van-icon name="user-o" size="14" />
            <span>登录</span>
          </router-link>
          <router-link to="/user" class="mi-login-btn logged-in" v-else>
            <van-icon name="user-o" size="14" />
            <span>我的</span>
          </router-link>
        </div>
      </div>
    </header>

    <!-- Tag Filter (Xiaomi category style) -->
    <div class="mi-tag-bar">
      <span
        v-for="tag in tags"
        :key="tag"
        :class="['mi-tag', { active: activeTag === tag }]"
        @click="toggleTag(tag)"
      >
        {{ tagIcons[tag] || '' }} {{ tag }}
      </span>
    </div>

    <!-- City Grid (Xiaomi product grid) -->
    <div class="mi-content">
      <van-loading v-if="loading" type="spinner" class="loading" />
      <van-empty v-else-if="cities.length === 0" description="暂无城市" />

      <div v-else class="mi-grid stagger">
        <div
          v-for="city in cities"
          :key="city.id"
          class="mi-card"
          @click="goDetail(city)"
        >
          <div class="mi-card-img" :style="{ background: cityBg(city.name) }">
            <img :src="city.cover_img" :alt="city.name" loading="lazy" />
            <span class="mi-card-img-letter">{{ city.name[0] }}</span>
            <div class="mi-card-badge" v-if="city.weather">
              <span v-if="city.weather.icon !== 'N/A'">
                {{ weatherEmoji(city.weather.icon) }} {{ city.weather.temp }}°
              </span>
              <span v-else>🌤 N/A</span>
            </div>
          </div>
          <div class="mi-card-body">
            <h3 class="mi-card-title">{{ city.name }}</h3>
            <div class="mi-card-tags">
              <span v-for="t in city.tags.slice(0, 3)" :key="t" class="mi-card-tag">{{ t }}</span>
            </div>
            <div class="mi-card-meta">{{ city.plan_days }}天路书</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Xiaomi-style Footer -->
    <footer class="mi-footer">
      <div class="mi-footer-inner">
        <div class="mi-footer-col">
          <h4>旅行服务</h4>
          <a href="/home">城市路书</a>
          <a href="/ai/plan">AI行程规划</a>
          <a href="/ai/ask">旅行问答</a>
        </div>
        <div class="mi-footer-col">
          <h4>用户服务</h4>
          <a href="/login">登录/注册</a>
          <a href="/user">个人中心</a>
        </div>
        <div class="mi-footer-col">
          <h4>关于</h4>
          <a href="/">关于我们</a>
        </div>
      </div>
      <div class="mi-footer-bottom">
        陆地旅行智能推荐系统 v3.2 &copy; 2026
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { fetchCities } from '@/api/cities'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const cities = ref([])
const loading = ref(false)
const keyword = ref('')
const activeTag = ref('')

const tags = ['文化', '美食', '亲子', '自驾', '自然']
const tagIcons = { '文化': '🏛️', '美食': '🍜', '亲子': '🧸', '自驾': '🚗', '自然': '🌿' }

const WEATHER_EMOJI = {
  '100': '☀️', '101': '⛅', '102': '🌤️', '104': '☁️',
  '300': '🌦️', '302': '⛈️', '305': '🌦️', '306': '🌧️',
  '400': '🌨️', '401': '❄️', '500': '🌫️',
}

function weatherEmoji(icon) { return WEATHER_EMOJI[icon] || '🌤️' }

async function loadCities() {
  loading.value = true
  try {
    const res = await fetchCities({
      tag: activeTag.value || undefined,
      search: keyword.value || undefined,
    })
    cities.value = res.data.items || []
  } catch (e) {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function onSearch() { loadCities() }
function toggleTag(tag) {
  activeTag.value = activeTag.value === tag ? '' : tag
  loadCities()
}
function goDetail(city) { router.push(`/city/${city.name}`) }

const PALETTES = [
  ['#667eea','#764ba2'],['#f093fb','#f5576c'],['#4facfe','#00f2fe'],
  ['#43e97b','#38f9d7'],['#fa709a','#fee140'],['#a18cd1','#fbc2eb'],
  ['#fccb90','#d57eeb'],['#30cfd0','#330867'],['#1fa2ff','#12d8fa'],
  ['#ff758c','#ff7eb3'],['#00b4db','#0083c8'],['#fc5c7d','#6a82fb'],
]

function hashColor(name) {
  let h = 0
  for (let i = 0; i < name.length; i++) { h = ((h << 5) - h) + name.charCodeAt(i); h |= 0 }
  return PALETTES[Math.abs(h) % PALETTES.length]
}

function cityBg(name) {
  const [c1, c2] = hashColor(name)
  return `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`
}

onMounted(loadCities)
</script>

<style scoped>
.mi-home { padding-bottom: 0; max-width: 1200px; margin: 0 auto; }

/* ===== Tag Bar ===== */
.mi-tag-bar {
  display: flex;
  gap: 8px;
  padding: 14px 20px 10px;
  overflow-x: auto;
  max-width: 1200px;
  margin: 0 auto;
}
.mi-tag-bar::-webkit-scrollbar { display: none; }
.mi-tag {
  flex-shrink: 0;
  padding: 6px 18px;
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border);
}
.mi-tag.active {
  color: #fff;
  background: var(--mi-orange);
  border-color: var(--mi-orange);
}

/* ===== Content ===== */
.mi-content { padding: 6px 20px; }
.loading { display: flex; justify-content: center; padding: 60px; }

/* ===== Xiaomi Product Grid ===== */
.mi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.mi-card {
  background: #fff;
  border-radius: 2px;
  cursor: pointer;
  transition: box-shadow 0.25s, transform 0.25s;
  overflow: hidden;
}
.mi-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.10);
  transform: translateY(-2px);
}
.mi-card:active { transform: scale(0.98); }

.mi-card-img {
  position: relative;
  width: 100%;
  padding-top: 66%;
  overflow: hidden;
}
.mi-card-img-letter {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  font-weight: 700;
  color: rgba(255,255,255,0.2);
  pointer-events: none;
}
.mi-card-img img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 2;
}

.mi-card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.mi-card-body {
  padding: 14px;
}
.mi-card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px;
  color: var(--mi-dark);
}
.mi-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}
.mi-card-tag {
  font-size: 11px;
  color: var(--text-hint);
  background: #f5f5f5;
  padding: 1px 8px;
  border-radius: 2px;
}
.mi-card-meta {
  font-size: 12px;
  color: var(--mi-orange);
}
</style>
