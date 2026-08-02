import axios from 'axios'

export interface ScanHistoryRecord {
  id: number
  filename: string
  language: string
  scan_mode: string
  rule_id: string | null
  rule_count: number
  finding_count: number
  status: string
  created_at: string
}

export interface ScanHistoryResponse {
  history: ScanHistoryRecord[]
}

const HISTORY_API_URL = 'http://127.0.0.1:8000/history'

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function safeString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback
}

function safeNullableString(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function safeNumber(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function normalizeRecord(value: unknown): ScanHistoryRecord {
  const record = isRecord(value) ? value : {}
  return {
    id: safeNumber(record.id, 0),
    filename: safeString(record.filename, 'unknown'),
    language: safeString(record.language, 'unknown'),
    scan_mode: safeString(record.scan_mode, 'all'),
    rule_id: safeNullableString(record.rule_id),
    rule_count: safeNumber(record.rule_count, 0),
    finding_count: safeNumber(record.finding_count, 0),
    status: safeString(record.status, 'success'),
    created_at: safeString(record.created_at, ''),
  }
}

export async function fetchScanHistory(): Promise<ScanHistoryResponse> {
  const response = await axios.get<unknown>(HISTORY_API_URL)

  if (!isRecord(response.data) || !Array.isArray(response.data.history)) {
    throw new Error('扫描历史 API 返回了无效的数据结构。')
  }

  return {
    history: response.data.history.map(normalizeRecord),
  }
}

export function readableHistoryApiError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error && error.message
      ? `无法连接本地扫描历史 API：${error.message}`
      : '无法连接本地扫描历史 API。'
  }

  if (!error.response) {
    return '无法连接本地扫描历史 API。请确认 FastAPI 已在 127.0.0.1:8000 启动，并通过 http://localhost:5173 打开前端。'
  }

  return `无法连接本地扫描历史 API（HTTP ${error.response.status}）。请检查本地后端服务。`
}
