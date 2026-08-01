<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import type { Severity } from '../types/dashboard'
import type { ReportRecord, ReportSeverity, ReportVulnerability } from '../types/reports'
import SeverityBadge from './SeverityBadge.vue'

const props = defineProps<{
  report: ReportRecord
}>()

const emit = defineEmits<{
  close: []
}>()

const severityOrder: ReportSeverity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']

const badgeSeverity: Record<ReportSeverity, Severity> = {
  CRITICAL: 'Critical',
  HIGH: 'High',
  MEDIUM: 'Medium',
  LOW: 'Low',
  UNKNOWN: 'Unknown',
}

const markdownContent = computed(() => generateMarkdown(props.report.vulnerabilities))
const jsonContent = computed(() => `${JSON.stringify({ vulnerabilities: props.report.vulnerabilities }, null, 2)}\n`)

function generateMarkdown(vulnerabilities: ReportVulnerability[]): string {
  const lines: string[] = ['# Security Report', '']

  for (const severity of severityOrder) {
    const findings = vulnerabilities.filter((item) => item.severity === severity)
    if (findings.length === 0) {
      continue
    }

    lines.push(`## ${severity} Risk`, '')

    findings.forEach((finding, index) => {
      if (index > 0) {
        lines.push('---', '')
      }

      lines.push(
        '漏洞:', '', finding.rule, '',
        'CWE:', '', finding.cwe || 'N/A', '',
        '类型:', '', finding.category || 'unknown', '',
        '文件:', '', finding.file || 'N/A', '',
        '行:', '', String(finding.line), '',
        '描述:', '', finding.description || '暂无描述', '',
        '修复建议:', '',
      )

      if (finding.fix.length > 0) {
        finding.fix.forEach((fix) => lines.push(`- ${fix}`))
      } else {
        lines.push('- 暂无修复建议')
      }
      lines.push('')
    })
  }

  return `${lines.join('\n').trimEnd()}\n`
}

function safeFileName(name: string): string {
  const normalized = name.trim().replace(/[\\/:*?"<>|\s]+/g, '-')
  return normalized || 'security-report'
}

const markdownDownloadUrl = URL.createObjectURL(
  new Blob([markdownContent.value], { type: 'text/markdown;charset=utf-8' }),
)
const jsonDownloadUrl = URL.createObjectURL(
  new Blob([jsonContent.value], { type: 'application/json;charset=utf-8' }),
)
const markdownFileName = `${safeFileName(props.report.name)}.md`
const jsonFileName = `${safeFileName(props.report.name)}.json`

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  URL.revokeObjectURL(markdownDownloadUrl)
  URL.revokeObjectURL(jsonDownloadUrl)
})
</script>

<template>
  <Teleport to="body">
    <div class="preview-layer" @click.self="emit('close')">
      <aside class="preview-panel" role="dialog" aria-modal="true" aria-labelledby="report-preview-title">
        <header class="preview-header">
          <div>
            <div class="preview-labels">
              <span>Local Preview</span>
              <b>{{ report.sourceLabel }}</b>
            </div>
            <h2 id="report-preview-title">{{ report.name }}</h2>
            <code>{{ report.scanTarget }}</code>
          </div>
          <button class="close-button" type="button" aria-label="关闭报告预览" @click="emit('close')">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </header>

        <div class="preview-content">
          <aside class="demo-notice">
            <strong>本地演示数据</strong>
            <p>此预览未连接报告历史 API，也不代表后端已保存扫描报告。</p>
          </aside>

          <dl class="report-meta">
            <div>
              <dt>Format</dt>
              <dd>{{ report.format }}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{{ report.status }}</dd>
            </div>
            <div>
              <dt>Generated At</dt>
              <dd>{{ report.generatedAt }}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{{ report.sourceLabel }}</dd>
            </div>
          </dl>

          <section class="findings-summary" aria-label="漏洞摘要">
            <div>
              <span>Total Findings</span>
              <strong>{{ report.findings }}</strong>
            </div>
            <div>
              <SeverityBadge severity="Critical" />
              <strong>{{ report.critical }}</strong>
            </div>
            <div>
              <SeverityBadge severity="High" />
              <strong>{{ report.high }}</strong>
            </div>
          </section>

          <section class="markdown-preview">
            <div class="section-heading">
              <div>
                <span>Markdown safety report</span>
                <h3>报告内容预览</h3>
              </div>
              <span class="local-tag">Local Preview</span>
            </div>
            <pre>{{ markdownContent }}</pre>
          </section>

          <div class="download-actions">
            <a :href="markdownDownloadUrl" :download="markdownFileName">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3v12m-4-4 4 4 4-4M5 19h14" />
              </svg>
              Download Markdown
            </a>
            <a class="secondary" :href="jsonDownloadUrl" :download="jsonFileName">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3v12m-4-4 4 4 4-4M5 19h14" />
              </svg>
              Download JSON
            </a>
          </div>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.preview-layer {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  justify-content: flex-end;
  background: rgba(17, 30, 45, .28);
}

.preview-panel {
  width: min(620px, 100%);
  height: 100%;
  overflow-y: auto;
  background: #f7f9fb;
  border-left: 1px solid #d8e0e8;
  box-shadow: -8px 0 28px rgba(24, 41, 59, .12);
}

.preview-header {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  background: rgba(255, 255, 255, .98);
  border-bottom: 1px solid var(--border-color);
}

.preview-labels {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-labels span,
.section-heading > div > span {
  color: var(--primary-color);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

.preview-labels b,
.local-tag {
  padding: 4px 7px;
  color: #6d6031;
  font-size: 9px;
  font-weight: 750;
  background: #f8f1d9;
  border: 1px solid #eadca9;
  border-radius: 5px;
}

.preview-header h2 {
  margin: 8px 0 6px;
  color: var(--heading-color);
  font-size: 20px;
}

.preview-header code {
  color: #58708b;
  font-family: var(--mono-font);
  font-size: 11px;
}

.close-button {
  display: grid;
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  place-items: center;
  color: #64758a;
  background: #f4f7f9;
  border: 1px solid #dce4eb;
  border-radius: 8px;
  cursor: pointer;
}

.close-button svg,
.download-actions svg {
  width: 17px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.preview-content {
  display: grid;
  gap: 18px;
  padding: 22px 24px 32px;
}

.demo-notice {
  padding: 14px 16px;
  background: #f8f4e7;
  border: 1px solid #e9dfbd;
  border-radius: 9px;
}

.demo-notice strong {
  color: #6e5c29;
  font-size: 11px;
}

.demo-notice p {
  margin: 5px 0 0;
  color: #7d7353;
  font-size: 11px;
  line-height: 1.55;
}

.report-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  margin: 0;
  overflow: hidden;
  background: #e1e7ed;
  border: 1px solid #e1e7ed;
  border-radius: 10px;
}

.report-meta div {
  min-width: 0;
  padding: 14px;
  background: #fff;
}

dt {
  color: #7d8c9d;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .06em;
  text-transform: uppercase;
}

dd {
  margin: 6px 0 0;
  overflow-wrap: anywhere;
  color: #33485f;
  font-family: var(--mono-font);
  font-size: 11px;
  font-weight: 650;
}

.findings-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.findings-summary > div {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 13px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 9px;
}

.findings-summary span:not(.severity-badge) {
  color: #6d7d90;
  font-size: 9px;
  font-weight: 700;
}

.findings-summary strong {
  color: var(--heading-color);
  font-size: 18px;
}

.markdown-preview {
  min-width: 0;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid #e7ecf1;
}

.section-heading h3 {
  margin: 5px 0 0;
  color: #34485e;
  font-size: 12px;
}

pre {
  max-height: 440px;
  margin: 0;
  padding: 18px;
  overflow: auto;
  color: #3d5268;
  font-family: var(--mono-font);
  font-size: 11px;
  line-height: 1.75;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #fbfcfd;
}

.download-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.download-actions a {
  display: flex;
  min-height: 42px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
  background: #526f8e;
  border: 1px solid #526f8e;
  border-radius: 8px;
  cursor: pointer;
}

.download-actions .secondary {
  color: #49647f;
  background: #fff;
  border-color: #ced9e3;
}

@media (max-width: 640px) {
  .preview-panel {
    width: 100%;
    border-left: 0;
  }

  .preview-header,
  .preview-content {
    padding-inline: 18px;
  }

  .findings-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 420px) {
  .report-meta,
  .download-actions {
    grid-template-columns: 1fr;
  }
}
</style>
