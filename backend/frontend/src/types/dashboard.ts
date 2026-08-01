export type MetricTone = 'critical' | 'high' | 'neutral' | 'primary'

export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'

export type FindingStatus = 'Open' | 'Reviewing' | 'Fixed'

export interface DashboardMetric {
  label: string
  value: number
  helper: string
  tone: MetricTone
}

export interface TrendPoint {
  label: string
  value: number
}

export interface DistributionItem {
  label: string
  value: number
  color: string
}

export interface RecentFinding {
  severity: Severity
  ruleId: string
  cwe: string
  file: string
  line: number
  status: FindingStatus
}

export interface ProjectSummary {
  name: string
  branch: string
  scanStatus: string
  scanTime: string
}

