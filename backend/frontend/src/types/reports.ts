export type ReportFormat = 'Markdown' | 'JSON'

export type ReportStatus = 'Ready' | 'Draft'

export type ReportFormatFilter = 'All' | ReportFormat

export type ReportStatusFilter = 'All' | ReportStatus

export type ReportSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN'

export interface ReportVulnerability {
  id: string
  rule: string
  file: string
  line: number
  category: string
  severity: ReportSeverity
  cwe: string
  description: string
  fix: string[]
}

export interface ReportRecord {
  id: string
  name: string
  scanTarget: string
  format: ReportFormat
  findings: number
  critical: number
  high: number
  generatedAt: string
  status: ReportStatus
  sourceLabel: 'Demo Data'
  vulnerabilities: ReportVulnerability[]
}
