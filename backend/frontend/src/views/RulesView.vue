<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RuleDetailPanel from '../components/RuleDetailPanel.vue'
import RuleFilters from '../components/RuleFilters.vue'
import SeverityBadge from '../components/SeverityBadge.vue'
import { fetchRuleCatalog, readableRuleApiError } from '../services/ruleApi'
import type { Severity } from '../types/dashboard'
import type {
  RuleCatalogItem,
  RuleCatalogState,
  RuleLanguage,
  RuleLanguageFilter,
  RuleSeverityFilter,
} from '../types/rules'

const languageFilter = ref<RuleLanguageFilter>('All')
const severityFilter = ref<RuleSeverityFilter>('All')
const categoryFilter = ref('All')
const query = ref('')
const rules = ref<RuleCatalogItem[]>([])
const loadState = ref<RuleCatalogState>('Loading')
const errorMessage = ref('')
const selectedRule = ref<RuleCatalogItem | null>(null)

const categories = computed(() => (
  Array.from(new Set(rules.value.map((rule) => rule.category))).sort()
))

const stats = computed(() => [
  { label: 'Total Rules', value: rules.value.length, helper: '来自本地 GET /rules', tone: 'total' },
  { label: 'PHP Rules', value: countLanguage('PHP'), helper: 'PHP 代码安全检测', tone: 'php' },
  { label: 'Python Rules', value: countLanguage('Python'), helper: 'Python 代码安全检测', tone: 'python' },
  { label: 'Java Rules', value: countLanguage('Java'), helper: 'Java 代码安全检测', tone: 'java' },
])

const filteredRules = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()

  return rules.value.filter((rule) => {
    const displayLanguage = formatLanguages(rule.languages)
    const displaySeverity = severityForBadge(rule.severity)
    const matchesLanguage = languageFilter.value === 'All'
      || hasLanguage(rule, languageFilter.value)
    const matchesSeverity = severityFilter.value === 'All'
      || displaySeverity === severityFilter.value
    const matchesCategory = categoryFilter.value === 'All' || rule.category === categoryFilter.value
    const matchesKeyword = keyword.length === 0
      || [rule.id, rule.cwe, displayLanguage].some(
        (value) => value.toLocaleLowerCase().includes(keyword),
      )

    return matchesLanguage && matchesSeverity && matchesCategory && matchesKeyword
  })
})

function normalizeLanguage(language: string): RuleLanguage | null {
  const normalized = language.trim().toLocaleLowerCase()
  const languageMap: Record<string, RuleLanguage> = {
    php: 'PHP',
    python: 'Python',
    java: 'Java',
    generic: 'Generic',
  }
  return languageMap[normalized] ?? null
}

function hasLanguage(rule: RuleCatalogItem, language: RuleLanguage): boolean {
  return rule.languages.some((item) => normalizeLanguage(item) === language)
}

function countLanguage(language: RuleLanguage): number {
  return rules.value.filter((rule) => hasLanguage(rule, language)).length
}

function formatLanguages(languages: string[]): string {
  if (!languages.length) return 'Unknown'
  return languages.map((language) => normalizeLanguage(language) ?? language).join(', ')
}

function severityForBadge(severity: RuleCatalogItem['severity']): Severity {
  const severityMap: Record<RuleCatalogItem['severity'], Severity> = {
    CRITICAL: 'Critical',
    HIGH: 'High',
    MEDIUM: 'Medium',
    LOW: 'Low',
    ERROR: 'High',
    WARNING: 'Medium',
    UNKNOWN: 'Unknown',
  }
  return severityMap[severity]
}

async function loadRules(): Promise<void> {
  loadState.value = 'Loading'
  errorMessage.value = ''
  selectedRule.value = null

  try {
    const response = await fetchRuleCatalog()
    rules.value = response.rules
    loadState.value = response.rules.length ? 'Success' : 'Empty'
  } catch (error: unknown) {
    rules.value = []
    loadState.value = 'Failed'
    errorMessage.value = readableRuleApiError(error)
  }
}

function resetFilters(): void {
  languageFilter.value = 'All'
  severityFilter.value = 'All'
  categoryFilter.value = 'All'
  query.value = ''
}

function openDetails(rule: RuleCatalogItem): void {
  selectedRule.value = rule
}

function closeDetails(): void {
  selectedRule.value = null
}

onMounted(loadRules)
</script>

<template>
  <section class="rules-view" aria-labelledby="rules-title">
    <header class="view-intro">
      <div>
        <span class="view-eyebrow">Local rule library</span>
        <h1 id="rules-title">安全规则库</h1>
        <p>查看当前项目内置的 Semgrep 规则、风险元数据与检测方式。</p>
      </div>
      <div class="library-state">
        <span class="state-dot" :class="`state-${loadState.toLowerCase()}`" aria-hidden="true"></span>
        <div>
          <span>规则 API</span>
          <strong>GET /rules</strong>
        </div>
      </div>
    </header>

    <section v-if="loadState === 'Loading'" class="request-state" role="status" aria-live="polite">
      <span class="loading-indicator" aria-hidden="true"></span>
      <div>
        <strong>正在读取本地规则库</strong>
        <p>正在连接 http://127.0.0.1:8000/rules</p>
      </div>
    </section>

    <section v-else-if="loadState === 'Failed'" class="request-state request-failed" role="alert">
      <div>
        <strong>无法连接本地规则库 API</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button type="button" @click="loadRules">Retry</button>
    </section>

    <section v-else-if="loadState === 'Empty'" class="request-state request-empty" aria-live="polite">
      <div>
        <strong>本地规则库暂无规则</strong>
        <p>GET /rules 已成功响应，但没有返回可展示的规则。</p>
      </div>
      <button type="button" @click="loadRules">重新加载</button>
    </section>

    <template v-else>
    <div class="stats-grid" aria-label="规则统计">
      <article v-for="stat in stats" :key="stat.label" class="stat-card" :class="`tone-${stat.tone}`">
        <div>
          <span>{{ stat.label }}</span>
          <i aria-hidden="true"></i>
        </div>
        <strong>{{ stat.value }}</strong>
        <p>{{ stat.helper }}</p>
      </article>
    </div>

    <RuleFilters
      :language="languageFilter"
      :severity="severityFilter"
      :category="categoryFilter"
      :query="query"
      :categories="categories"
      :result-count="filteredRules.length"
      @update:language="languageFilter = $event"
      @update:severity="severityFilter = $event"
      @update:category="categoryFilter = $event"
      @update:query="query = $event"
      @reset="resetFilters"
    />

    <section class="rules-table-card" aria-label="规则列表">
      <div class="table-heading">
        <div>
          <span class="section-kicker">Semgrep rules</span>
          <h2>已加载规则</h2>
        </div>
        <span>点击列表项查看规则详情</span>
      </div>

      <div v-if="filteredRules.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Rule ID</th>
              <th>Language</th>
              <th>Category</th>
              <th>CWE</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="rule in filteredRules"
              :key="rule.id"
              tabindex="0"
              @click="openDetails(rule)"
              @keydown.enter="openDetails(rule)"
            >
              <td><SeverityBadge :severity="severityForBadge(rule.severity)" /></td>
              <td class="rule-id">{{ rule.id }}</td>
              <td><span class="language-tag">{{ formatLanguages(rule.languages) }}</span></td>
              <td>{{ rule.category }}</td>
              <td class="mono muted">{{ rule.cwe }}</td>
              <td class="description" :title="rule.description">{{ rule.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-state">
        <strong>没有匹配的规则</strong>
        <p>调整语言、风险或关键词条件后重试。</p>
        <button type="button" @click="resetFilters">清除筛选</button>
      </div>
    </section>
    </template>

    <RuleDetailPanel v-if="selectedRule" :rule="selectedRule" @close="closeDetails" />
  </section>
</template>

<style scoped>
.rules-view {
  width: min(100%, 1520px);
  margin: 0 auto;
  padding: clamp(24px, 3vw, 40px);
}

.view-intro {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 26px;
}

.view-eyebrow,
.section-kicker {
  display: block;
  color: var(--primary-color);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

.view-intro h1 {
  margin: 8px 0 0;
  color: var(--heading-color);
  font-size: clamp(1.65rem, 2.1vw, 2.15rem);
  line-height: 1.2;
  letter-spacing: -.035em;
}

.view-intro p {
  margin: 9px 0 0;
  color: var(--muted-text);
  font-size: 13px;
}

.request-state {
  display: flex;
  min-height: 220px;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 32px;
  text-align: left;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.request-state strong {
  color: #3b5067;
  font-size: 14px;
}

.request-state p {
  margin: 7px 0 0;
  color: #7b8999;
  font-size: 12px;
  line-height: 1.6;
}

.request-state button {
  padding: 9px 14px;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  background: #526f8e;
  border: 1px solid #486784;
  border-radius: 7px;
  cursor: pointer;
}

.request-failed {
  justify-content: space-between;
  color: #8d3941;
  background: #fffafb;
  border-color: #eccfd3;
}

.request-failed strong {
  color: #8d3941;
}

.request-empty {
  justify-content: space-between;
}

.loading-indicator {
  width: 19px;
  height: 19px;
  flex: 0 0 19px;
  border: 2px solid #d8e1e9;
  border-top-color: #5b7896;
  border-radius: 50%;
  animation: loading-rotate .8s linear infinite;
}

@keyframes loading-rotate {
  to { transform: rotate(360deg); }
}

.library-state {
  display: flex;
  align-items: center;
  gap: 10px;
}

.state-dot {
  width: 9px;
  height: 9px;
  background: #649078;
  border-radius: 50%;
}

.state-loading { background: #7189a5; }
.state-success { background: #649078; }
.state-failed { background: #bd4b54; }
.state-empty { background: #b1933d; }

.library-state div {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}

.library-state span {
  color: var(--muted-text);
  font-size: 10px;
}

.library-state strong {
  color: #40566d;
  font-family: var(--mono-font);
  font-size: 11px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.stat-card {
  padding: 18px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.stat-card > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #607186;
  font-size: 11px;
  font-weight: 650;
}

.stat-card i {
  width: 8px;
  height: 8px;
  background: #7189a5;
  border-radius: 3px;
}

.tone-php i { background: #6a839f; }
.tone-python i { background: #b1933d; }
.tone-java i { background: #b46745; }

.stat-card > strong {
  display: block;
  margin-top: 13px;
  color: var(--heading-color);
  font-size: 30px;
  line-height: 1;
}

.stat-card p {
  margin: 8px 0 0;
  color: var(--muted-text);
  font-size: 10px;
}

.rules-table-card {
  min-width: 0;
  margin-top: 18px;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.table-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px 17px;
}

.table-heading h2 {
  margin: 5px 0 0;
  color: var(--heading-color);
  font-size: 16px;
}

.table-heading > span {
  color: #8997a7;
  font-size: 10px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 960px;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 16px;
  text-align: left;
  border-top: 1px solid #edf0f4;
}

th {
  color: #7d8b9b;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .06em;
  text-transform: uppercase;
  background: #fafbfd;
}

td {
  color: #43566b;
  font-size: 11px;
}

tbody tr {
  cursor: pointer;
  outline: none;
}

tbody tr:hover,
tbody tr:focus-visible {
  background: #f7fafc;
}

tbody tr:focus-visible {
  box-shadow: inset 3px 0 0 #6f89a6;
}

.rule-id,
.mono {
  font-family: var(--mono-font);
}

.rule-id {
  color: #385470;
  font-weight: 650;
}

.muted {
  color: #718196;
}

.language-tag {
  padding: 4px 7px;
  color: #536b84;
  font-size: 10px;
  font-weight: 700;
  background: #edf2f6;
  border-radius: 5px;
}

.description {
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  display: grid;
  min-height: 250px;
  place-content: center;
  justify-items: center;
  padding: 32px;
  text-align: center;
  border-top: 1px solid #edf0f4;
}

.empty-state strong {
  color: #3b5067;
  font-size: 14px;
}

.empty-state p {
  margin: 7px 0 14px;
  color: #7b8999;
  font-size: 12px;
}

.empty-state button {
  padding: 8px 12px;
  color: #496681;
  background: #edf3f7;
  border: 1px solid #d9e3eb;
  border-radius: 7px;
  cursor: pointer;
}

@media (max-width: 1080px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .rules-view {
    padding: 20px 16px 28px;
  }

  .view-intro {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 22px;
  }

  .library-state div {
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .table-heading {
    padding-inline: 16px;
  }

  .request-state {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
