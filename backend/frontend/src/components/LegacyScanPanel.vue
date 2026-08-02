<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import ScanRuleSelector from './ScanRuleSelector.vue'
import ScanResultsTable from './ScanResultsTable.vue'
import VulnerabilityDetailPanel from './VulnerabilityDetailPanel.vue'
import { fetchRuleCatalog, readableRuleApiError } from '../services/ruleApi'
import type {
  ScanStatus,
  Severity,
  VulnerabilityRecord,
} from '../types/dashboard'
import type { RuleCatalogItem, RuleCatalogState } from '../types/rules'

type UnknownRecord = Record<string, unknown>
type SupportedLanguage = 'PHP' | 'Python' | 'Java'
type ScanMode = 'all' | 'single'

const SCAN_URL = 'http://127.0.0.1:8000/scan'

const EXTENSION_LANGUAGE_MAP: Record<string, SupportedLanguage> = {

  php: 'PHP',
  py: 'Python',
  java: 'Java',
}

interface CompletedScan {
  mode: ScanMode
  language: string
  ruleCount: number
  ruleId: string
  sourceFile: string
}


const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const detectedLanguage = ref<SupportedLanguage | ''>('')
const status = ref<ScanStatus>('Idle')
const errorMessage = ref('')
const findings = ref<VulnerabilityRecord[]>([])
const selectedFinding = ref<VulnerabilityRecord | null>(null)
const dragActive = ref(false)
const allRules = ref<RuleCatalogItem[]>([])
const selectedRuleId = ref('')
const ruleLoadState = ref<RuleCatalogState>('Loading')
const ruleErrorMessage = ref('')
const completedScan = ref<CompletedScan | null>(null)
const scanMode = ref<ScanMode>('all')

const isBusy = computed(() => status.value === 'Uploading' || status.value === 'Scanning')

const rules = computed<RuleCatalogItem[]>(() => {
  if (!detectedLanguage.value) return allRules.value

  const language = detectedLanguage.value.toLowerCase()
  return allRules.value.filter((rule) => (
    rule.languages.some((item) => item.trim().toLowerCase() === language)
  ))
})

const selectedRule = computed(() => (
  rules.value.find((rule) => rule.id === selectedRuleId.value) ?? null
))

// 全部规则模式下无需选择单条规则。
const canScan = computed(() => (
  Boolean(selectedFile.value)
  && Boolean(detectedLanguage.value)
  && ruleLoadState.value === 'Success'
  && rules.value.length > 0
  && (scanMode.value === 'all' || Boolean(selectedRule.value))
  && !isBusy.value
))

const scanModeHint = computed(() => {

  if (!detectedLanguage.value || !rules.value.length) return ''
  if (scanMode.value === 'all') {
    return `将运行 ${detectedLanguage.value} 规则 ${rules.value.length} 条`
  }
  return selectedRule.value
    ? `将运行单条规则：${selectedRule.value.id}`
    : '请选择一条规则'
})


const statusCopy: Record<ScanStatus, { label: string; detail: string }> = {
  Idle: { label: 'Idle', detail: '选择源代码文件，系统会自动识别语言并筛选规则' },
  Uploading: { label: 'Uploading', detail: '正在上传文件到本地扫描服务' },
  Scanning: { label: 'Scanning', detail: 'Semgrep 正在执行规则分析' },
  Completed: { label: 'Completed', detail: '扫描完成，结果已返回' },
  Failed: { label: 'Failed', detail: '扫描未完成，请查看错误信息' },
}

const selectedFileSize = computed(() => {
  if (!selectedFile.value) return ''
  if (selectedFile.value.size < 1024) return `${selectedFile.value.size} B`
  return `${(selectedFile.value.size / 1024).toFixed(1)} KB`
})

const selectedFileTypeLabel = computed(() => (
  detectedLanguage.value ? `${detectedLanguage.value} source file` : 'source file'
))

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function safeString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback
}

function safeLine(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

function normalizeFixes(value: unknown): string[] {
  if (typeof value === 'string' && value.trim()) return [value.trim()]
  if (!Array.isArray(value)) return ['暂无修复建议']

  const fixes = value.filter((item): item is string => typeof item === 'string' && Boolean(item.trim()))
  return fixes.length ? fixes : ['暂无修复建议']
}

function normalizeSeverity(value: unknown): Severity {
  const normalized = typeof value === 'string' ? value.trim().toUpperCase() : ''
  const severityMap: Record<string, Severity> = {
    CRITICAL: 'Critical',
    HIGH: 'High',
    MEDIUM: 'Medium',
    LOW: 'Low',
  }
  return severityMap[normalized] ?? 'Unknown'
}

function normalizeFinding(value: unknown, index: number, sourceFile: string): VulnerabilityRecord {
  const finding = isRecord(value) ? value : {}
  const ruleId = safeString(finding.rule, safeString(finding.id, 'unknown-rule'))
  const description = safeString(
    finding.description,
    safeString(finding.message, '暂无描述'),
  )

  return {
    id: safeString(finding.id, `${ruleId}-${index}`),
    name: description === '暂无描述' ? ruleId : description,
    severity: normalizeSeverity(finding.severity),
    ruleId,
    cwe: safeString(finding.cwe, 'N/A'),
    category: safeString(finding.category, 'unknown'),
    language: safeString(
      finding.language,
      detectedLanguage.value || selectedRule.value?.languages?.[0] || 'Unknown',
    ),
    file: safeString(finding.file, sourceFile),
    line: safeLine(finding.line),
    status: 'Open',
    description,
    fixes: normalizeFixes(finding.fix),
    codeSnippet: safeString(finding.code_snippet, '暂无代码片段'),
    patchStatus: 'PENDING',
  }
}


function normalizeResponse(value: unknown, sourceFile: string): VulnerabilityRecord[] {
  if (!isRecord(value) || !Array.isArray(value.vulnerabilities)) return []
  return value.vulnerabilities.map((finding, index) => normalizeFinding(finding, index, sourceFile))
}

function normalizeCompletedScan(value: unknown): CompletedScan {
  const response = isRecord(value) ? value : {}
  const scanInfo = isRecord(response.scan) ? response.scan : {}
  const mode = scanInfo.mode === 'single' ? 'single' : 'all'
  return {
    mode,
    language: safeString(scanInfo.language, detectedLanguage.value),
    ruleCount: typeof scanInfo.rule_count === 'number' ? scanInfo.rule_count : rules.value.length,
    ruleId: safeString(scanInfo.rule_id, selectedRuleId.value),
    sourceFile: safeString(scanInfo.source_file, selectedRule.value?.source_file ?? 'unknown'),
  }
}


function extractErrorDetail(value: unknown): string {
  if (typeof value === 'string' && value.trim()) return value.trim()
  if (!isRecord(value)) return ''

  if (typeof value.detail === 'string') return value.detail
  if (Array.isArray(value.detail)) {
    const messages = value.detail
      .map((item) => isRecord(item) ? safeString(item.msg, '') : '')
      .filter(Boolean)
    return messages.join('；')
  }
  return ''
}

function readableScanError(error: unknown): string {
  if (!axios.isAxiosError(error)) return '扫描失败，请稍后重试。'

  if (!error.response) {
    return '无法连接扫描服务。请确认 FastAPI 已在 127.0.0.1:8000 启动，并通过 http://localhost:5173 打开前端。'
  }

  const detail = extractErrorDetail(error.response.data)
  return `扫描失败（HTTP ${error.response.status}）${detail ? `：${detail}` : '，请检查后端日志。'}`
}

function detectLanguage(file: File): SupportedLanguage | '' {
  const extension = file.name.split('.').pop()?.trim().toLowerCase() ?? ''
  return EXTENSION_LANGUAGE_MAP[extension] ?? ''
}

function resetScanResult(): void {
  errorMessage.value = ''
  findings.value = []
  selectedFinding.value = null
  completedScan.value = null
}

function selectDefaultRule(availableRules: RuleCatalogItem[]): void {
  // 若当前已选择的规则不在新上传文件语言的可用规则中，则自动清空选择。
  const currentRuleStillAvailable = availableRules.some((rule) => rule.id === selectedRuleId.value)
  if (!currentRuleStillAvailable) {
    selectedRuleId.value = ''
  }
}


function setFile(file: File | null): void {
  resetScanResult()

  if (!file) {
    selectedFile.value = null
    detectedLanguage.value = ''
    selectDefaultRule(allRules.value)
    status.value = 'Idle'
    return
  }

  const language = detectLanguage(file)
  if (!language) {
    selectedFile.value = null
    detectedLanguage.value = ''
    selectDefaultRule(allRules.value)
    status.value = 'Failed'
    errorMessage.value = '当前仅支持 .php、.py、.java 文件。'
    return
  }

  selectedFile.value = file
  detectedLanguage.value = language
  selectDefaultRule(rules.value)

  if (!rules.value.length) {
    status.value = 'Failed'
    errorMessage.value = `已识别为 ${language}，但规则库中没有可用的 ${language} 规则。`
    return
  }

  status.value = 'Idle'
}

function chooseFile(event: Event): void {
  const input = event.target as HTMLInputElement
  setFile(input.files?.[0] ?? null)
  input.value = ''
}

function handleDrop(event: DragEvent): void {
  dragActive.value = false
  setFile(event.dataTransfer?.files?.[0] ?? null)
}

function openFilePicker(): void {
  if (!isBusy.value) fileInput.value?.click()
}

function setScanMode(mode: ScanMode): void {
  if (isBusy.value) return
  if (mode === scanMode.value) return

  scanMode.value = mode
  resetScanResult()
  status.value = 'Idle'
}

async function scan(): Promise<void> {
  const file = selectedFile.value
  const rule = selectedRule.value
  if (!file || !canScan.value) return
  if (scanMode.value === 'single' && !rule) return

  const formData = new FormData()
  formData.append('file', file)
  formData.append('scan_mode', scanMode.value)
  if (scanMode.value === 'single' && rule) {
    formData.append('rule_id', rule.id)
  }

  resetScanResult()
  status.value = 'Uploading'

  try {
    const response = await axios.post<unknown>(SCAN_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const uploadFinished = progressEvent.progress === 1
          || (typeof progressEvent.total === 'number' && progressEvent.loaded >= progressEvent.total)
        if (uploadFinished) status.value = 'Scanning'
      },
    })

    findings.value = normalizeResponse(response.data, file.name)
    completedScan.value = normalizeCompletedScan(response.data)
    status.value = 'Completed'
  } catch (error: unknown) {
    status.value = 'Failed'
    errorMessage.value = readableScanError(error)
  }
}

function selectRule(ruleId: string): void {
  if (isBusy.value) return

  const ruleIsAvailable = rules.value.some((rule) => rule.id === ruleId)
  if (!ruleIsAvailable) return

  selectedRuleId.value = ruleId
  resetScanResult()
  status.value = 'Idle'
}


async function loadRules(): Promise<void> {
  ruleLoadState.value = 'Loading'
  ruleErrorMessage.value = ''
  allRules.value = []
  selectedRuleId.value = ''

  try {
    const response = await fetchRuleCatalog()
    allRules.value = response.rules

    if (!allRules.value.length) {
      ruleLoadState.value = 'Empty'
      return
    }

    selectDefaultRule(rules.value)
    ruleLoadState.value = 'Success'
  } catch (error: unknown) {
    ruleLoadState.value = 'Failed'
    ruleErrorMessage.value = readableRuleApiError(error)
  }
}

function closeDetails(): void {
  selectedFinding.value = null
}

onMounted(loadRules)
</script>


<template>
  <section class="scan-panel" aria-labelledby="upload-title">
    <div class="panel-heading">
      <div>
        <span class="section-kicker">Scan target</span>
        <h2 id="upload-title">上传待扫描代码</h2>
        <p>上传后自动识别 PHP、Python 或 Java，并仅显示对应规则。</p>
      </div>
      <div class="endpoint-badge">
        <span>POST</span>
        <code>/scan</code>
      </div>
    </div>

    <div
      class="drop-zone"
      :class="{ 'drag-active': dragActive, disabled: isBusy }"
      role="button"
      :tabindex="isBusy ? -1 : 0"
      aria-label="选择或拖放代码文件"
      @click="openFilePicker"
      @keydown.enter="openFilePicker"
      @keydown.space.prevent="openFilePicker"
      @dragenter.prevent="dragActive = true"
      @dragover.prevent="dragActive = true"
      @dragleave.prevent="dragActive = false"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".php,.py,.java"
        hidden
        @change="chooseFile"
      >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v5h14v-5" />
      </svg>
      <template v-if="selectedFile">
        <strong>{{ selectedFile.name }}</strong>
        <span>{{ selectedFileSize }} · {{ selectedFileTypeLabel }}</span>
      </template>
      <template v-else>
        <strong>拖拽代码文件到这里，或点击选择</strong>
        <span>支持单个 .php / .py / .java 文件</span>
      </template>
    </div>

    <div v-if="selectedFile && detectedLanguage" class="language-summary" aria-live="polite">
      <div>
        <span class="language-label">检测语言</span>
        <strong>{{ detectedLanguage }}</strong>
      </div>
      <div>
        <span class="language-label">适用规则</span>
        <strong>{{ rules.length }} 条</strong>
      </div>
    </div>

    <div v-if="selectedFile && detectedLanguage" class="scan-mode-card" aria-live="polite">
      <div class="scan-mode-options">
        <label class="scan-mode-option" :class="{ active: scanMode === 'all' }">
          <input
            type="radio"
            name="scan-mode"
            value="all"
            :checked="scanMode === 'all'"
            :disabled="isBusy"
            @change="setScanMode('all')"
          >
          <span>
            <strong>全部适用规则</strong>
            <small>默认，一次扫描该语言全部规则</small>
          </span>
        </label>
        <label class="scan-mode-option" :class="{ active: scanMode === 'single' }">
          <input
            type="radio"
            name="scan-mode"
            value="single"
            :checked="scanMode === 'single'"
            :disabled="isBusy"
            @change="setScanMode('single')"
          >
          <span>
            <strong>指定单条规则</strong>
            <small>手动选择一条规则进行扫描</small>
          </span>
        </label>
      </div>
      <p v-if="scanModeHint" class="scan-mode-hint">{{ scanModeHint }}</p>
    </div>

    <ScanRuleSelector
      v-if="scanMode === 'single'"
      :state="ruleLoadState"
      :rules="rules"
      :selected-rule-id="selectedRuleId"
      :error-message="ruleErrorMessage"
      :disabled="isBusy"
      @update:selected-rule-id="selectRule"
      @retry="loadRules"
    />

    <div
      v-if="selectedFile && detectedLanguage && ruleLoadState === 'Success' && !rules.length"
      class="error-message"
      role="alert"
    >
      <strong>没有匹配规则</strong>
      <p>规则库中暂时没有适用于 {{ detectedLanguage }} 的规则。</p>
    </div>

    <div class="scan-controls">
      <div class="status-block" :class="`status-${status.toLowerCase()}`" aria-live="polite">
        <span class="status-dot" aria-hidden="true"></span>
        <div>
          <strong>{{ statusCopy[status].label }}</strong>
          <span>{{ statusCopy[status].detail }}</span>
        </div>
      </div>
      <button class="scan-button" type="button" :disabled="!canScan" @click="scan">
        {{ isBusy ? statusCopy[status].label : 'Start Scan' }}
      </button>
    </div>


    <div v-if="errorMessage" class="error-message" role="alert">
      <strong>扫描失败</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <section v-if="status === 'Completed'" class="scan-results" aria-labelledby="scan-results-title">
      <div class="results-heading">
        <div>
          <span class="section-kicker">Scan results</span>
          <h2 id="scan-results-title">本次扫描结果</h2>
          <p v-if="completedScan" class="completed-rule">
            <template v-if="completedScan.mode === 'all'">
              规则集：{{ completedScan.language }} 全部规则（{{ completedScan.ruleCount }} 条）
            </template>
            <template v-else>
              Rule: <code>{{ completedScan.ruleId }}</code> · Source: <code>{{ completedScan.sourceFile }}</code>
            </template>
          </p>


        </div>
        <div class="result-count">
          <strong>{{ findings.length }}</strong>
          <span>findings</span>
        </div>
      </div>

      <ScanResultsTable
        v-if="findings.length"
        :findings="findings"
        @select="selectedFinding = $event"
      />
      <div v-else class="clean-result">
        <strong>未发现匹配漏洞</strong>
        <p v-if="completedScan?.mode === 'all'">
          {{ completedScan.language }} 全部规则（{{ completedScan.ruleCount }} 条）未在该文件中发现匹配漏洞。
        </p>
        <p v-else>
          所选规则 {{ completedScan?.ruleId ?? selectedRuleId }} 未在该文件中发现匹配漏洞。
        </p>
      </div>

    </section>

    <VulnerabilityDetailPanel
      v-if="selectedFinding"
      :vulnerability="selectedFinding"
      @close="closeDetails"
    />
  </section>
</template>

<style scoped>
.scan-panel {
  display: grid;
  gap: 18px;
}

.panel-heading,
.scan-controls,
.results-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.panel-heading {
  padding: 22px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.section-kicker {
  display: block;
  color: var(--primary-color);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

h2 {
  margin: 6px 0 0;
  color: var(--heading-color);
  font-size: 16px;
}

.panel-heading p {
  margin: 7px 0 0;
  color: var(--muted-text);
  font-size: 11px;
}

.endpoint-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  background: #f1f5f8;
  border: 1px solid #dce5ed;
  border-radius: 7px;
}

.endpoint-badge span {
  color: #47725f;
  font-size: 9px;
  font-weight: 800;
}

.endpoint-badge code {
  color: #4d6279;
  font-family: var(--mono-font);
  font-size: 10px;
}

.drop-zone {
  display: grid;
  min-height: 230px;
  place-content: center;
  justify-items: center;
  padding: 30px;
  color: #64778b;
  text-align: center;
  background: #fff;
  border: 1px dashed #b9c7d4;
  border-radius: var(--card-radius);
  outline: none;
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone:focus-visible,
.drop-zone.drag-active {
  background: #f8fafc;
  border-color: #7892ad;
}

.drop-zone.disabled {
  cursor: default;
  opacity: .65;
}

.drop-zone svg {
  width: 32px;
  margin-bottom: 15px;
  fill: none;
  stroke: #6f88a3;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.5;
}

.drop-zone strong {
  color: #344b62;
  font-size: 14px;
}

.drop-zone span {
  margin-top: 7px;
  color: #8593a3;
  font-size: 11px;
}

.scan-controls {
  padding: 17px 18px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
}

.status-block {
  display: flex;
  align-items: center;
  gap: 11px;
}

.status-dot {
  width: 9px;
  height: 9px;
  flex: 0 0 9px;
  background: #94a1b0;
  border-radius: 50%;
}

.status-block > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.status-block strong {
  color: #3c5067;
  font-family: var(--mono-font);
  font-size: 11px;
}

.status-block span:last-child {
  color: #8190a1;
  font-size: 10px;
}

.status-uploading .status-dot,
.status-scanning .status-dot {
  background: #6785a4;
}

.status-completed .status-dot {
  background: #599076;
}

.status-failed .status-dot {
  background: #bd4b54;
}

.scan-button {
  min-width: 118px;
  padding: 10px 16px;
  color: #fff;
  font-size: 11px;
  font-weight: 750;
  background: #4f6f91;
  border: 1px solid #456584;
  border-radius: 8px;
  cursor: pointer;
}

.scan-button:disabled {
  color: #9ba7b4;
  background: #e7ebef;
  border-color: #dde3e8;
}

.error-message {
  padding: 16px 18px;
  color: #8d3941;
  background: #fbebed;
  border: 1px solid #f0cfd3;
  border-radius: 9px;
}

.error-message strong {
  font-size: 12px;
}

.error-message p {
  margin: 5px 0 0;
  font-size: 11px;
  line-height: 1.6;
}

.scan-results {
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.results-heading {
  padding: 20px 22px 18px;
}

.result-count {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.result-count strong {
  color: var(--heading-color);
  font-size: 24px;
}

.result-count span {
  color: #8290a0;
  font-size: 10px;
  text-transform: uppercase;
}

.completed-rule {
  margin: 7px 0 0;
  color: #748397;
  font-size: 10px;
}

.completed-rule code {
  color: #4f6882;
  font-family: var(--mono-font);
}

.clean-result {
  padding: 34px 22px;
  text-align: center;
  border-top: 1px solid #edf0f4;
}

.clean-result strong {
  color: #3e715d;
  font-size: 13px;
}

.clean-result p {
  margin: 7px 0 0;
  color: #7b8999;
  font-size: 11px;
}


.language-summary {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 15px 18px;
  background: #f8fafc;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
}

.language-summary > div {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.language-label {
  color: #7c8b9d;
  font-size: 10px;
}

.language-summary strong {
  color: #3f5872;
  font-family: var(--mono-font);
  font-size: 12px;
}

.scan-mode-card {
  padding: 15px 18px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
}

.scan-mode-options {
  display: flex;
  gap: 12px;
}

.scan-mode-option {
  display: flex;
  flex: 1;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8ef;
  border-radius: 9px;
  cursor: pointer;
}

.scan-mode-option.active {
  background: #eef4fb;
  border-color: #9db8d6;
}

.scan-mode-option input {
  margin-top: 3px;
  accent-color: #4f6f91;
}

.scan-mode-option > span {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.scan-mode-option strong {
  color: #3c5067;
  font-size: 12px;
}

.scan-mode-option small {
  color: #8190a1;
  font-size: 10px;
}

.scan-mode-hint {
  margin: 12px 0 0;
  padding: 9px 12px;
  color: #4f6882;
  font-size: 11px;
  background: #f1f5f8;
  border-radius: 7px;
}

@media (max-width: 640px) {
  .panel-heading,
  .scan-controls,
  .language-summary {
    align-items: flex-start;
    flex-direction: column;
  }

  .scan-mode-options {
    flex-direction: column;
  }


  .endpoint-badge {
    align-self: flex-start;
  }

  .drop-zone {
    min-height: 190px;
    padding-inline: 18px;
  }

  .scan-button {
    width: 100%;
  }
}
</style>
