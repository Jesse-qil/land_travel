<template>
  <div class="page ai-plan-page" style="padding: 20px;">
    <van-nav-bar title="AI 行程生成" left-arrow @click-left="router.back()" />

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-card" style="margin-bottom:16px; padding:16px; background:#fff; border-left:4px solid #ee0a24; border-radius:4px;">
      <p style="margin:0 0 8px; font-size:15px;">{{ errorMsg }}</p>
      <button @click="errorMsg = ''; aiStore.clearPlan()" style="padding:6px 20px; background:#ff6900; color:#fff; border:none; border-radius:2px; font-size:14px; cursor:pointer;">重试</button>
    </div>

    <!-- 生成表单 -->
    <div v-if="!aiStore.generatedPlan && !aiStore.generating && !errorMsg">
      <h2 style="font-size:20px; text-align:center; margin-bottom:6px;">🎯 定制你的专属行程</h2>
      <p style="font-size:14px; text-align:center; color:#999; margin-bottom:20px;">AI 将基于实时天气、景点状态为你智能规划</p>

      <div style="background:#fff; border-radius:4px; padding:16px; margin-bottom:16px;">
        <div style="margin-bottom:14px;">
          <label style="font-size:14px; color:#333; display:block; margin-bottom:4px;">📍 城市</label>
          <input v-model="form.city" placeholder="如：北京、成都、杭州" style="width:100%; padding:10px; border:1px solid #e5e5e5; border-radius:2px; font-size:15px; outline:none;" />
        </div>
        <div style="margin-bottom:14px;">
          <label style="font-size:14px; color:#333; display:block; margin-bottom:4px;">📅 天数</label>
          <div style="display:flex; gap:8px;">
            <button @click="form.days = Math.max(1, form.days - 1)" style="width:36px; height:36px; border:1px solid #e5e5e5; background:#f5f5f5; border-radius:2px; cursor:pointer; font-size:18px;">−</button>
            <span style="width:50px; text-align:center; line-height:36px; font-size:16px;">{{ form.days }}</span>
            <button @click="form.days = Math.min(7, form.days + 1)" style="width:36px; height:36px; border:1px solid #e5e5e5; background:#f5f5f5; border-radius:2px; cursor:pointer; font-size:18px;">+</button>
          </div>
        </div>
        <div style="margin-bottom:14px;">
          <label style="font-size:14px; color:#333; display:block; margin-bottom:4px;">💰 预算</label>
          <div style="display:flex; gap:10px;">
            <label v-for="b in ['low','medium','high']" :key="b" :style="{padding:'6px 16px', border:'1px solid #e5e5e5', borderRadius:'2px', cursor:'pointer', background: form.budget === b ? '#ff6900' : '#fff', color: form.budget === b ? '#fff' : '#333', fontSize:'14px'}" @click="form.budget = b">{{ {low:'经济',medium:'舒适',high:'豪华'}[b] }}</label>
          </div>
        </div>
        <div style="margin-bottom:14px;">
          <label style="font-size:14px; color:#333; display:block; margin-bottom:4px;">👥 同行人</label>
          <input v-model="form.companions" placeholder="独自 / 情侣 / 朋友 / 家庭" style="width:100%; padding:10px; border:1px solid #e5e5e5; border-radius:2px; font-size:15px; outline:none;" />
        </div>
      </div>

      <button @click="onGenerate" :disabled="aiStore.generating" style="width:100%; padding:14px; background:#ff6900; color:#fff; border:none; border-radius:2px; font-size:16px; cursor:pointer;">
        {{ aiStore.generating ? 'AI 生成中...' : '生成智能行程' }}
      </button>
      <p style="font-size:12px; text-align:center; color:#999; margin-top:12px;">AI 基于实时天气、景点状态生成，约 10-30 秒</p>
    </div>

    <!-- 生成中 -->
    <div v-if="aiStore.generating" style="text-align:center; padding:60px 20px;">
      <div style="font-size:40px; margin-bottom:16px;">🧠</div>
      <p style="font-size:17px; font-weight:600;">AI 正在思考...</p>
      <p style="font-size:14px; color:#999;">正在获取实时天气与景点状态</p>
    </div>

    <!-- 生成结果 -->
    <div v-if="aiStore.generatedPlan && !aiStore.generating">
      <div style="display:flex; justify-content:space-between; align-items:center; padding:16px; background:#fff;">
        <div>
          <span style="display:inline-block; font-size:12px; font-weight:600; color:#fff; background:#ff6900; padding:2px 10px; border-radius:2px; margin-bottom:6px;">AI 智能生成</span>
          <h2 style="font-size:17px; font-weight:700; margin:0;">{{ form.city }} · {{ form.days }}日行程</h2>
        </div>
        <button @click="aiStore.clearPlan()" style="padding:6px 14px; border:1px solid #ff6900; color:#ff6900; background:transparent; border-radius:2px; cursor:pointer; font-size:13px;">重新生成</button>
      </div>

      <div v-if="aiStore.planWarnings.length" style="font-size:13px; color:#faab0c; padding:8px 16px; background:#fff8e6;">
        {{ aiStore.planWarnings[0] }}
      </div>

      <div v-if="budgetEstimate" style="text-align:center; padding:14px; margin:12px; background:linear-gradient(135deg,#fffbe8,#fff8d6); border:1px solid #ffe58f; border-radius:4px; font-size:15px; color:#d48806;">
        预估总费用：<strong>约 ¥{{ budgetEstimate }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { useAiStore } from '@/stores/ai'

const router = useRouter()
const aiStore = useAiStore()

const form = reactive({
  city: '',
  days: 3,
  budget: 'medium',
  style: [],
  companions: '独自',
})

const activeDay = ref(0)
const genStep = ref(1)
const errorMsg = ref('')

const planDays = computed(() => aiStore.generatedPlan?.items || [])
const currentDay = computed(() => planDays.value[activeDay.value])
const budgetEstimate = computed(() => aiStore.generatedPlan?.budget_estimate)

const DAY_COLORS = ['#1989fa', '#07c160', '#ee0a24', '#7232dd', '#faab0c', '#f06', '#07c160']
function dayColor(d) { return DAY_COLORS[(d - 1) % DAY_COLORS.length] }

async function onGenerate() {
  if (!form.city.trim()) {
    showToast('请输入城市')
    return
  }
  genStep.value = 1
  const timer = setInterval(() => {
    if (genStep.value < 3) genStep.value++
  }, 3000)

  try {
    await aiStore.generatePlan({
      city: form.city,
      days: form.days,
      budget: form.budget,
      style: form.style,
      companions: form.companions,
    })
    activeDay.value = 0
    if (aiStore.generatedPlan) {
      showToast('✅ 行程已生成')
    }
  } catch (e) {
    errorMsg.value = e?.message || 'AI 服务暂不可用，请确认 Agent 服务已启动（端口 8001）'
    showFailToast('⚠️ ' + (e?.message || 'AI 服务异常'))
  } finally {
    clearInterval(timer)
  }
}
</script>

<style scoped>
.ai-plan-page { background: var(--bg-page); min-height: 100vh; }

/* ===== Error card ===== */
.error-card {
  display: flex;
  gap: 14px;
  margin: 20px 16px;
  padding: 18px;
  background: #fff;
  border-radius: 14px;
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--danger);
  animation: fadeInUp 0.3s ease;
}
.error-card :deep(.van-icon-warn-o) {
  font-size: 28px;
  color: var(--danger);
  flex-shrink: 0;
  margin-top: 2px;
}
.error-body { flex: 1; }
.error-body strong {
  display: block;
  font-size: 16px;
  margin-bottom: 6px;
  color: var(--text-primary);
}
.error-body p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px;
  line-height: 1.5;
}
.error-actions { display: flex; gap: 8px; }

/* ===== 表单区 ===== */
.form-section { padding: 0 0 20px; }

.form-header {
  text-align: center;
  padding: 24px 20px 16px;
}
.form-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
}
.form-desc {
  font-size: 15px;
  color: var(--text-hint);
  margin: 0;
}

.form-group {
  margin: 0 12px;
  border-radius: 14px;
  overflow: hidden;
}

.form-group :deep(.van-cell) {
  padding: 14px 16px;
}

.budget-radio { margin-right: 8px; }
.budget-radio :deep(.van-radio__label) { font-size: 13px; }

.style-checkbox { margin-right: 8px; margin-bottom: 4px; }
.style-checkbox :deep(.van-checkbox__label) { font-size: 13px; }

.submit-wrap {
  padding: 16px 20px;
}

.tips-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-hint);
  padding: 0 20px;
  background: #f5f7fa;
  margin: 0 20px;
  border-radius: 10px;
  padding: 10px 16px;
}

/* ===== 加载动画 ===== */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px 40px;
  gap: 16px;
}

.loading-animation {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loader-ring {
  position: absolute;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 4px solid #e8edf0;
  border-top-color: var(--mi-orange);
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loader-icon { font-size: 32px; z-index: 1; animation: pulse 1.5s ease infinite; }

.loading-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.loading-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 220px;
}
.step {
  font-size: 15px;
  color: var(--text-hint);
  padding: 6px 14px;
  border-radius: 20px;
  background: #f0f2f5;
  text-align: center;
  transition: all 0.3s;
}
.step.active {
  color: #fff;
  background: linear-gradient(135deg, var(--mi-orange), var(--primary-dark));
  box-shadow: 0 4px 12px rgba(255,105,0,0.25);
  font-weight: 500;
}

.loading-hint {
  font-size: 14px;
  color: var(--text-hint);
  animation: pulse 1.5s ease infinite;
}

/* ===== 结果区 ===== */
.result-section { padding-bottom: 20px; }

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  background: #fff;
  position: sticky;
  top: 46px;
  z-index: 9;
}
.result-badge {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  margin-bottom: 6px;
}
.result-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
}

.warnings {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff8e6;
  padding: 8px 16px;
  font-size: 14px;
  color: #faab0c;
}

.day-plan { padding: 12px; }

.day-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
}

.day-weather {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  color: var(--mi-orange);
  margin-bottom: 16px;
  background: #f0f7ff;
  padding: 6px 12px;
  border-radius: 8px;
}

/* 景点列表 */
.spot-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.spot-card {
  display: flex;
  gap: 12px;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: var(--shadow-sm);
  animation: fadeInUp 0.4s ease both;
}

.spot-index {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}

.spot-body { flex: 1; min-width: 0; }
.spot-name { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.spot-activity { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }

.spot-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.meta-item {
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 8px;
  background: #f0f2f5;
  color: var(--text-secondary);
}
.tag-success { background: #e8f8ee; color: var(--success); font-weight: 500; }
.tag-na { background: #fff8e6; color: #d48806; }

.spot-tip {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 14px;
  color: var(--text-hint);
}

/* 预算条 */
.budget-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px;
  font-size: 15px;
  color: #d48806;
  background: linear-gradient(135deg, #fffbe8, #fff8d6);
  margin: 12px;
  border-radius: 12px;
  border: 1px solid #ffe58f;
}
</style>
