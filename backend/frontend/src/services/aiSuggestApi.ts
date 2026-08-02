import axios from 'axios'

export interface AISuggestion {
  summary: string
  risk: string
  root_cause: string
  suggested_code: string
  steps: string[]
  caveats: string[]
}

export interface AISuggestResponse {
  suggestion: AISuggestion
  cached: boolean
  remaining_requests: number
  used_budget_usd: number
  daily_budget_usd: number
}

export interface AISuggestRequest {
  client_id: string
  filename: string
  language: string
  rule_id: string
  severity: string
  cwe: string
  category: string
  description: string
  code_snippet: string
  rule_fix: string[]
}

const SUGGEST_API_URL = 'http://127.0.0.1:8000/ai/suggest-fix'

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function safeString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback
}

function safeNumber(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function safeStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value
    .filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
    .map((item) => item.trim())
}

function normalizeSuggestion(value: unknown): AISuggestion {
  const record = isRecord(value) ? value : {}
  return {
    summary: safeString(record.summary, ''),
    risk: safeString(record.risk, ''),
    root_cause: safeString(record.root_cause, ''),
    suggested_code: safeString(record.suggested_code, ''),
    steps: safeStringArray(record.steps),
    caveats: safeStringArray(record.caveats),
  }
}

export async function fetchAISuggestion(
  request: AISuggestRequest,
): Promise<AISuggestResponse> {
  const response = await axios.post<unknown>(SUGGEST_API_URL, request)

  if (!isRecord(response.data)) {
    throw new Error('AI 建议 API 返回了无效的数据结构。')
  }

  return {
    suggestion: normalizeSuggestion(response.data.suggestion),
    cached: response.data.cached === true,
    remaining_requests: safeNumber(response.data.remaining_requests, 0),
    used_budget_usd: safeNumber(response.data.used_budget_usd, 0),
    daily_budget_usd: safeNumber(response.data.daily_budget_usd, 0),
  }
}

export function readableAISuggestError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error && error.message
      ? `无法获取 AI 修复建议：${error.message}`
      : '无法获取 AI 修复建议。'
  }

  if (!error.response) {
    return '无法连接本地 AI 服务。请确认 FastAPI 已在 127.0.0.1:8000 启动。'
  }

  const status = error.response.status
  const detail = isRecord(error.response.data)
    ? safeString(error.response.data.detail, '')
    : ''

  if (status === 503) {
    return 'AI 修复建议服务未配置。请在 .env 中设置 OPENROUTER_API_KEY 后重启后端。'
  }
  if (status === 429) {
    return detail || '今日 AI 请求次数或费用额度已达上限，请明天再试。'
  }
  if (status === 400) {
    return detail || 'AI 修复建议请求参数无效。'
  }
  if (status === 502) {
    // 后端对截断/非法 JSON 返回简洁提示，直接展示，不暴露原始模型内容。
    return detail || 'AI 服务暂时不可用，请稍后重试。'
  }
  return `无法获取 AI 修复建议（HTTP ${status}）。`

}
