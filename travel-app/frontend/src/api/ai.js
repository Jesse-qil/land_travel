import client from './client'

/** AI 行程生成 */
export function generatePlan(data) {
  return client.post('/ai/plan', data, { timeout: 60000 })
}

/** AI 多轮问答 */
export function askQuestion(data) {
  return client.post('/ai/ask', data, { timeout: 60000 })
}
