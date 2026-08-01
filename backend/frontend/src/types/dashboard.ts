export type MetricTone = 'critical' | 'high' | 'neutral' | 'primary'

export type Severity = 'Critical' | 'High' | 'Medium' | 'Low'

export type FindingStatus = 'Open' | 'Reviewing' | 'Fixed'

export type AppView = 'dashboard' | 'vulnerabilities'

export type VulnerabilityLanguage = 'PHP' | 'Python' | 'Java'

export type PatchVerificationStatus = 'FIXED' | 'PENDING'

export type SeverityFilter = 'All' | Extract<Severity, 'Critical' | 'High' | 'Medium'>

export type LanguageFilter = 'All' | VulnerabilityLanguage

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

export interface VulnerabilityRecord {
  id: string
  name: string
  severity: Severity
  ruleId: string
  cwe: string
  category: string
  language: VulnerabilityLanguage
  file: string
  line: number
  status: FindingStatus
  description: string
  fixes: string[]
  patchStatus: PatchVerificationStatus
}
