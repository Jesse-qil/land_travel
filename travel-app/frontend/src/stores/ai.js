import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as aiApi from '@/api/ai'

export const useAiStore = defineStore('ai', () => {
  const generating = ref(false)
  const generatedPlan = ref(null)
  const planWarnings = ref([])
  const askSessionId = ref(null)
  const messages = ref([])
  const asking = ref(false)
  const contextExpireAt = ref(null)

  async function generatePlan(params) {
    generating.value = true
    generatedPlan.value = null
    planWarnings.value = []
    try {
      const res = await aiApi.generatePlan(params)
      generatedPlan.value = res.data.plan
      planWarnings.value = res.data.warnings || []
      return res.data
    } finally {
      generating.value = false
    }
  }

  async function ask(question) {
    asking.value = true
    messages.value.push({ role: 'user', content: question })
    try {
      const res = await aiApi.askQuestion({
        session_id: askSessionId.value,
        question,
      })
      askSessionId.value = res.data.session_id
      contextExpireAt.value = res.data.context_expire_at
      messages.value.push({ role: 'assistant', content: res.data.answer })
      return res.data.answer
    } catch (e) {
      messages.value.push({ role: 'assistant', content: '（回复失败，请重试）' })
      throw e
    } finally {
      asking.value = false
    }
  }

  function clearChat() {
    messages.value = []
    askSessionId.value = null
    contextExpireAt.value = null
  }

  function clearPlan() {
    generatedPlan.value = null
    planWarnings.value = []
  }

  return {
    generating,
    generatedPlan,
    planWarnings,
    askSessionId,
    messages,
    asking,
    contextExpireAt,
    generatePlan,
    ask,
    clearChat,
    clearPlan,
  }
})
