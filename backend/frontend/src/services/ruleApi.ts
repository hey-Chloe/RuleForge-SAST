import axios from 'axios'
import type {
  RuleCatalogItem,
  RuleCatalogResponse,
  RuleCatalogSeverity,
} from '../types/rules'

type UnknownRecord = Record<string, unknown>

const RULES_API_URL = 'http://127.0.0.1:8000/rules'

const supportedSeverities = new Set<RuleCatalogSeverity>([
  'CRITICAL',
  'HIGH',
  'MEDIUM',
  'LOW',
  'ERROR',
  'WARNING',
  'UNKNOWN',
])

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function safeString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback
}

function safeStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.filter(
    (item): item is string => typeof item === 'string' && Boolean(item.trim()),
  ).map((item) => item.trim())
}

function safeSeverity(value: unknown, fallback: RuleCatalogSeverity): RuleCatalogSeverity {
  const normalized = typeof value === 'string' ? value.trim().toUpperCase() : ''
  return supportedSeverities.has(normalized as RuleCatalogSeverity)
    ? normalized as RuleCatalogSeverity
    : fallback
}

function normalizeRule(value: unknown): RuleCatalogItem {
  const rule = isRecord(value) ? value : {}
  const semgrepSeverity = safeSeverity(rule.semgrep_severity, 'UNKNOWN')
  const message = safeString(rule.message, '')

  return {
    id: safeString(rule.id, 'unknown-rule'),
    languages: safeStringList(rule.languages),
    message,
    semgrep_severity: semgrepSeverity,
    category: safeString(rule.category, 'unknown'),
    severity: safeSeverity(rule.severity, semgrepSeverity),
    cwe: safeString(rule.cwe, 'N/A'),
    description: safeString(rule.description, message),
    fix: safeStringList(rule.fix),
    source_file: safeString(rule.source_file, 'unknown'),
  }
}

export async function fetchRuleCatalog(): Promise<RuleCatalogResponse> {
  const response = await axios.get<unknown>(RULES_API_URL)

  if (!isRecord(response.data) || !Array.isArray(response.data.rules)) {
    throw new Error('规则库 API 返回了无效的数据结构。')
  }

  return {
    rules: response.data.rules.map(normalizeRule),
  }
}

export function readableRuleApiError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error && error.message
      ? `无法连接本地规则库 API：${error.message}`
      : '无法连接本地规则库 API。'
  }

  if (!error.response) {
    return '无法连接本地规则库 API。请确认 FastAPI 已在 127.0.0.1:8000 启动，并通过 http://localhost:5173 打开前端。'
  }

  return `无法连接本地规则库 API（HTTP ${error.response.status}）。请检查本地后端服务。`
}
