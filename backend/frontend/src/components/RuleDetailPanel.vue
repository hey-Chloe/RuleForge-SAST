<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import SeverityBadge from './SeverityBadge.vue'
import type { Severity } from '../types/dashboard'
import type { RuleCatalogItem, RuleDetectionMethod } from '../types/rules'

const props = defineProps<{
  rule: RuleCatalogItem
}>()

const emit = defineEmits<{
  close: []
}>()

const taintRuleIds = new Set([
  'php-ssrf-user-controlled-url',
  'php-reflected-xss',
  'php-user-controlled-upload-name',
])

const detectionMethod = computed<RuleDetectionMethod>(() => {
  if (taintRuleIds.has(props.rule.id)) return 'Taint Analysis'
  if (props.rule.id === 'hardcoded-secret') return 'Regex Pattern'
  if (props.rule.id === 'java-sql-injection') return 'Direct Pattern'
  return 'Direct API Detection'
})

const detectionSummary = computed(() => {
  if (detectionMethod.value === 'Taint Analysis') {
    return '该规则使用 Semgrep taint mode 跟踪明确的 source 到 sink 数据流。'
  }
  if (detectionMethod.value === 'Regex Pattern') {
    return '该规则使用正则表达式匹配特定的危险代码形式。'
  }
  if (detectionMethod.value === 'Direct Pattern') {
    return '初版直接模式检测，匹配 SQL 字符串拼接后进入 Statement 执行方法的场景。'
  }
  return '该规则直接匹配已知的高风险 API 或代码调用形式。'
})

const detectionClass = computed(() => {
  if (detectionMethod.value === 'Taint Analysis') return 'method-taint'
  if (detectionMethod.value === 'Regex Pattern') return 'method-regex'
  return 'method-direct'
})

const displaySeverity = computed<Severity>(() => {
  const severityMap: Record<RuleCatalogItem['severity'], Severity> = {
    CRITICAL: 'Critical',
    HIGH: 'High',
    MEDIUM: 'Medium',
    LOW: 'Low',
    ERROR: 'High',
    WARNING: 'Medium',
    UNKNOWN: 'Unknown',
  }
  return severityMap[props.rule.severity]
})

const displayLanguages = computed(() => {
  const languageLabels: Record<string, string> = {
    php: 'PHP',
    python: 'Python',
    java: 'Java',
    generic: 'Generic',
  }
  return props.rule.languages.length
    ? props.rule.languages.map(
      (language) => languageLabels[language.toLocaleLowerCase()] ?? language,
    ).join(', ')
    : 'Unknown'
})

const usesMetadataDefaults = computed(() => (
  props.rule.category === 'unknown'
  || props.rule.cwe === 'N/A'
  || props.rule.fix.length === 0
))

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <Teleport to="body">
    <div class="detail-layer" @click.self="emit('close')">
      <aside class="detail-panel" role="dialog" aria-modal="true" aria-labelledby="rule-detail-title">
        <header class="detail-header">
          <div>
            <span class="detail-kicker">Rule details</span>
            <h2 id="rule-detail-title">{{ rule.id }}</h2>
            <span class="source-badge">Local Rule Library</span>
          </div>
          <button type="button" aria-label="关闭规则详情" @click="emit('close')">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </header>

        <div class="detail-content">
          <div class="risk-row">
            <SeverityBadge :severity="displaySeverity" />
            <span class="detection-badge" :class="detectionClass">{{ detectionMethod }}</span>
          </div>

          <dl class="detail-grid">
            <div>
              <dt>Language</dt>
              <dd>{{ displayLanguages }}</dd>
            </div>
            <div>
              <dt>Category</dt>
              <dd>{{ rule.category }}</dd>
            </div>
            <div>
              <dt>CWE</dt>
              <dd>{{ rule.cwe }}</dd>
            </div>
            <div>
              <dt>Semgrep Severity</dt>
              <dd>{{ rule.semgrep_severity }}</dd>
            </div>
          </dl>

          <section class="detail-section">
            <h3>中文漏洞描述</h3>
            <p>{{ rule.description || '暂无描述' }}</p>
          </section>

          <section class="detail-section">
            <h3>修复建议</h3>
            <ul v-if="rule.fix.length">
              <li v-for="fix in rule.fix" :key="fix">{{ fix }}</li>
            </ul>
            <p v-else>暂无修复建议</p>
          </section>

          <section class="detail-section">
            <h3>Semgrep Message</h3>
            <p>{{ rule.message || '暂无消息' }}</p>
          </section>

          <section class="detection-card">
            <div>
              <span>检测方式</span>
              <strong>{{ detectionMethod }}</strong>
            </div>
            <p>{{ detectionSummary }}</p>
          </section>

          <section class="source-card">
            <div>
              <span>Source File</span>
              <strong>Local Rule Library</strong>
            </div>
            <code>{{ rule.source_file }}</code>
            <p v-if="usesMetadataDefaults">该规则使用 API 提供的 metadata 安全默认值，缺失内容不会影响展示。</p>
          </section>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.detail-layer {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  justify-content: flex-end;
  background: rgba(17, 30, 45, .28);
}

.detail-panel {
  width: min(500px, 100%);
  height: 100%;
  overflow-y: auto;
  background: #f7f9fb;
  border-left: 1px solid #d8e0e8;
  box-shadow: -8px 0 28px rgba(24, 41, 59, .12);
}

.detail-header {
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

.detail-kicker {
  color: var(--primary-color);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

.detail-header h2 {
  margin: 7px 0 8px;
  color: var(--heading-color);
  font-family: var(--mono-font);
  font-size: 18px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.source-badge {
  display: inline-flex;
  padding: 5px 8px;
  color: #4c685d;
  font-size: 9px;
  font-weight: 750;
  background: #eaf2ee;
  border-radius: 5px;
}

.detail-header button {
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

.detail-header svg {
  width: 17px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 1.8;
}

.detail-content {
  display: grid;
  gap: 18px;
  padding: 22px 24px 32px;
}

.risk-row,
.detection-card div,
.source-card div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detection-badge {
  padding: 6px 9px;
  font-size: 9px;
  font-weight: 750;
  border-radius: 6px;
}

.method-taint {
  color: #8e4f2e;
  background: #faece3;
}

.method-direct {
  color: #4e6680;
  background: #eaf0f5;
}

.method-regex {
  color: #6d5d86;
  background: #f0edf5;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  margin: 0;
  overflow: hidden;
  background: #e1e7ed;
  border: 1px solid #e1e7ed;
  border-radius: 10px;
}

.detail-grid div {
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
  color: #33485f;
  font-family: var(--mono-font);
  font-size: 11px;
  font-weight: 650;
}

.detail-section,
.detection-card,
.source-card {
  padding: 18px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.detail-section h3 {
  margin: 0 0 11px;
  color: #34485e;
  font-size: 12px;
}

.detail-section p,
.detail-section li,
.detection-card p,
.source-card p {
  color: #617186;
  font-size: 12px;
  line-height: 1.7;
}

.detail-section p,
.detection-card p,
.source-card p {
  margin: 0;
}

.detail-section ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

.detection-card span,
.source-card span {
  color: #7b8999;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: .05em;
  text-transform: uppercase;
}

.detection-card strong,
.source-card strong {
  color: #3e5870;
  font-size: 11px;
}

.detection-card p {
  margin-top: 9px;
}

.source-card code {
  display: block;
  margin-top: 10px;
  padding: 9px 10px;
  color: #526982;
  font-family: var(--mono-font);
  font-size: 10px;
  overflow-wrap: anywhere;
  background: #f4f7f9;
  border-radius: 6px;
}

.source-card p {
  margin-top: 10px;
  color: #886d2a;
}

@media (max-width: 640px) {
  .detail-panel {
    width: 100%;
    border-left: 0;
  }

  .detail-header,
  .detail-content {
    padding-inline: 18px;
  }
}
</style>
