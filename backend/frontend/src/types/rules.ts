import type { Severity } from './dashboard'

export type RuleLanguage = 'PHP' | 'Python' | 'Java' | 'Generic'

export type RuleDetectionMethod =
  | 'Direct API Detection'
  | 'Taint Analysis'
  | 'Direct Pattern'
  | 'Regex Pattern'

export type RuleLanguageFilter = 'All' | RuleLanguage

export type RuleSeverityFilter = 'All' | Extract<Severity, 'Critical' | 'High' | 'Medium'>

export interface RuleRecord {
  id: string
  language: RuleLanguage
  severity: Severity
  semgrepSeverity: 'ERROR' | 'WARNING'
  category: string
  cwe: string
  description: string
  fixes: string[]
  detectionMethod: RuleDetectionMethod
  detectionSummary: string
  source: 'Local Rule Library'
  sourceFile: string
  metadataAvailable: boolean
}

export type RuleCatalogSeverity =
  | 'CRITICAL'
  | 'HIGH'
  | 'MEDIUM'
  | 'LOW'
  | 'ERROR'
  | 'WARNING'
  | 'UNKNOWN'

export interface RuleCatalogItem {
  id: string
  languages: string[]
  message: string
  semgrep_severity: RuleCatalogSeverity
  category: string
  severity: RuleCatalogSeverity
  cwe: string
  description: string
  fix: string[]
  source_file: string
}

export interface RuleCatalogResponse {
  rules: RuleCatalogItem[]
}

export type RuleCatalogState = 'Loading' | 'Success' | 'Failed' | 'Empty'
