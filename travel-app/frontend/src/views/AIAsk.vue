<template>
  <div class="page ai-ask-page">
    <van-nav-bar title="AI 旅行问答" left-arrow @click-left="router.back()">
      <template #right>
        <van-icon name="delete-o" size="20" color="#969799" @click="onClear" v-if="aiStore.messages.length" />
      </template>
    </van-nav-bar>

    <div class="chat-area" ref="chatArea">
      <!-- 欢迎页 -->
      <div v-if="!aiStore.messages.length" class="welcome fade-in">
        <div class="welcome-icon">💬</div>
        <h2 class="welcome-title">旅行问题随便问</h2>
        <p class="welcome-desc">景点推荐 · 行程规划 · 美食 · 交通 · 天气</p>
        <div class="suggestions">
          <div
            v-for="q in suggestions"
            :key="q"
            class="suggest-chip"
            @click="quickAsk(q)"
          >
            <span class="suggest-icon">{{ suggestIcon(q) }}</span>
            {{ q }}
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(msg, idx) in aiStore.messages"
        :key="idx"
        :class="['message', msg.role, { 'fade-in-up': idx === aiStore.messages.length - 1 || idx === aiStore.messages.length - 2 }]"
      >
        <div class="msg-avatar" :class="msg.role">
          {{ msg.role === 'user' ? '🧑' : '🤖' }}
        </div>
        <div class="msg-content">
          <div class="msg-bubble">{{ msg.content }}</div>
          <div class="msg-time">{{ msg.role === 'user' ? '你' : 'AI' }} · 刚刚</div>
        </div>
      </div>

      <!-- 思考中 -->
      <div v-if="aiStore.asking" class="message assistant fade-in">
        <div class="msg-avatar assistant">🤖</div>
        <div class="msg-content">
          <div class="msg-bubble thinking">
            <span class="dot dot1">.</span>
            <span class="dot dot2">.</span>
            <span class="dot dot3">.</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 上下文提示 -->
    <div class="context-tip" v-if="aiStore.contextExpireAt">
      <van-icon name="clock-o" />
      <span>上下文 10 分钟内有效</span>
    </div>

    <!-- 输入栏 -->
    <div class="input-bar">
      <van-field
        v-model="inputText"
        placeholder="输入旅行问题..."
        :disabled="aiStore.asking"
        @keyup.enter="onSend"
        clearable
      />
      <van-button
        round
        type="primary"
        :loading="aiStore.asking"
        :disabled="!inputText.trim()"
        @click="onSend"
        class="send-btn"
      >
        发送
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAiStore } from '@/stores/ai'

const router = useRouter()
const aiStore = useAiStore()

const inputText = ref('')
const chatArea = ref(null)

const suggestions = [
  '北京 3 天怎么玩？',
  '成都亲子游推荐',
  '西安美食有哪些？',
  '杭州雨天适合去哪？',
]

function suggestIcon(q) {
  if (/怎么玩|行程/.test(q)) return '🗺️'
  if (/亲子/.test(q)) return '🧸'
  if (/美食/.test(q)) return '🍜'
  if (/雨天/.test(q)) return '🌧️'
  return '💡'
}

async function onSend() {
  const q = inputText.value.trim()
  if (!q) return
  inputText.value = ''
  try {
    await aiStore.ask(q)
  } catch (e) {
    showToast(e?.message || '回复失败')
  }
}

function quickAsk(q) {
  inputText.value = q
  onSend()
}

function onClear() {
  aiStore.clearChat()
}

watch(() => aiStore.messages.length, async () => {
  await nextTick()
  if (chatArea.value) {
    chatArea.value.scrollTop = chatArea.value.scrollHeight
  }
})
</script>

<style scoped>
.ai-ask-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  padding-bottom: 0;
}

/* ===== 聊天区域 ===== */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px 14px;
  scroll-behavior: smooth;
}

/* ===== 欢迎页 ===== */
.welcome {
  text-align: center;
  padding: 40px 20px 20px;
}
.welcome-icon { font-size: 56px; margin-bottom: 12px; }
.welcome-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
}
.welcome-desc {
  font-size: 15px;
  color: var(--text-hint);
  margin: 0 0 24px;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 320px;
  margin: 0 auto;
}
.suggest-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1.5px solid transparent;
}
.suggest-chip:hover {
  border-color: var(--primary-light);
  color: var(--mi-orange);
  transform: translateX(4px);
}
.suggest-chip:active {
  transform: scale(0.97);
}
.suggest-icon { font-size: 18px; }

/* ===== 消息 ===== */
.message {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  align-items: flex-start;
}
.message.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.msg-avatar.assistant {
  background: linear-gradient(135deg, #e8f0fe, #d4e4fc);
}
.msg-avatar.user {
  background: linear-gradient(135deg, #d4f5e8, #b8efd6);
}

.msg-content {
  max-width: 75%;
  min-width: 60px;
}

.msg-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.message.assistant .msg-bubble {
  background: #fff;
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow-sm);
}

.message.user .msg-bubble {
  background: linear-gradient(135deg, var(--mi-orange), var(--primary-dark));
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-time {
  font-size: 13px;
  color: var(--text-hint);
  margin-top: 4px;
  padding: 0 4px;
}
.message.user .msg-time {
  text-align: right;
}

/* 思考中动画 */
.thinking {
  display: flex;
  gap: 2px;
  padding: 14px 20px !important;
  align-items: center;
}
.dot {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-hint);
  line-height: 1;
}
.dot1 { animation: pulse 1.2s ease infinite; }
.dot2 { animation: pulse 1.2s ease infinite 0.2s; }
.dot3 { animation: pulse 1.2s ease infinite 0.4s; }

/* ===== 上下文提示 ===== */
.context-tip {
  text-align: center;
  font-size: 13px;
  color: #c8c9cc;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: #fff;
  border-top: 1px solid var(--border);
}

/* ===== 输入栏 ===== */
.input-bar {
  display: flex;
  gap: 8px;
  padding: 8px 12px 12px;
  background: #fff;
  border-top: 1px solid var(--border);
  align-items: center;
}

.input-bar :deep(.van-field) {
  flex: 1;
  background: #f0f2f5;
  border-radius: 22px;
  padding: 6px 14px;
  border: 1.5px solid transparent;
  transition: border-color 0.2s;
}
.input-bar :deep(.van-field:focus-within) {
  border-color: var(--primary-light);
}
.input-bar :deep(.van-field__body) {
  background: transparent;
}

.send-btn {
  flex-shrink: 0;
  padding: 0 18px;
  height: 38px;
}
</style>
