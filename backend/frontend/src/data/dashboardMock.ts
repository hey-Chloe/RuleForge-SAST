import type {
  DashboardMetric,
  DistributionItem,
  ProjectSummary,
  RecentFinding,
  TrendPoint,
} from '../types/dashboard'

export const projectSummary: ProjectSummary = {
  name: 'RuleForge-SAST',
  branch: 'main',
  scanStatus: '最近扫描已完成',
  scanTime: '2 分钟前',
}

export const dashboardMetrics: DashboardMetric[] = [
  {
    label: 'Critical Vulnerabilities',
    value: 3,
    helper: '较上次扫描减少 1 项',
    tone: 'critical',
  },
  {
    label: 'High Risk',
    value: 7,
    helper: '4 项等待修复验证',
    tone: 'high',
  },
  {
    label: 'Total Findings',
    value: 24,
    helper: '覆盖 3 种代码语言',
    tone: 'neutral',
  },
  {
    label: 'Rules Loaded',
    value: 18,
    helper: '规则库状态正常',
    tone: 'primary',
  },
]

export const trendPoints: TrendPoint[] = [
  { label: '06-01', value: 17 },
  { label: '06-08', value: 22 },
  { label: '06-15', value: 19 },
  { label: '06-22', value: 31 },
  { label: '06-29', value: 28 },
  { label: '07-06', value: 26 },
  { label: '07-13', value: 24 },
]

export const vulnerabilityDistribution: DistributionItem[] = [
  { label: 'Deserialization', value: 6, color: '#6f86a6' },
  { label: 'RCE', value: 5, color: '#d45d62' },
  { label: 'XSS', value: 4, color: '#d58a48' },
  { label: 'SQL Injection', value: 3, color: '#b9a153' },
  { label: 'File Upload', value: 2, color: '#708c82' },
  { label: 'Other', value: 4, color: '#a2adbd' },
]

export const recentFindings: RecentFinding[] = [
  {
    severity: 'Critical',
    ruleId: 'php-dangerous-eval',
    cwe: 'CWE-95',
    file: 'src/Controller/DebugController.php',
    line: 48,
    status: 'Open',
  },
  {
    severity: 'High',
    ruleId: 'java-unsafe-deserialization',
    cwe: 'CWE-502',
    file: 'service/ImportService.java',
    line: 76,
    status: 'Reviewing',
  },
  {
    severity: 'High',
    ruleId: 'php-ssrf-user-controlled-url',
    cwe: 'CWE-918',
    file: 'app/Services/WebhookClient.php',
    line: 113,
    status: 'Open',
  },
  {
    severity: 'Medium',
    ruleId: 'php-weak-hash',
    cwe: 'CWE-328',
    file: 'app/Support/Token.php',
    line: 29,
    status: 'Fixed',
  },
  {
    severity: 'Medium',
    ruleId: 'php-weak-randomness',
    cwe: 'CWE-330',
    file: 'app/Auth/ResetCode.php',
    line: 64,
    status: 'Reviewing',
  },
]
