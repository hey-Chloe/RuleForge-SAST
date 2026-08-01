<script setup lang="ts">
import { computed, ref } from 'vue'
import RuleDetailPanel from '../components/RuleDetailPanel.vue'
import RuleFilters from '../components/RuleFilters.vue'
import SeverityBadge from '../components/SeverityBadge.vue'
import { ruleLibrary } from '../data/rulesMock'
import type { RuleLanguageFilter, RuleRecord, RuleSeverityFilter } from '../types/rules'

const languageFilter = ref<RuleLanguageFilter>('All')
const severityFilter = ref<RuleSeverityFilter>('All')
const categoryFilter = ref('All')
const query = ref('')
const selectedRule = ref<RuleRecord | null>(null)

const categories = Array.from(new Set(ruleLibrary.map((rule) => rule.category))).sort()

const stats = [
  { label: 'Total Rules', value: ruleLibrary.length, helper: '包含 1 条 Generic 规则', tone: 'total' },
  { label: 'PHP Rules', value: ruleLibrary.filter((rule) => rule.language === 'PHP').length, helper: 'PHP 代码安全检测', tone: 'php' },
  { label: 'Python Rules', value: ruleLibrary.filter((rule) => rule.language === 'Python').length, helper: 'Python 代码安全检测', tone: 'python' },
  { label: 'Java Rules', value: ruleLibrary.filter((rule) => rule.language === 'Java').length, helper: 'Java 代码安全检测', tone: 'java' },
]

const filteredRules = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()

  return ruleLibrary.filter((rule) => {
    const matchesLanguage = languageFilter.value === 'All' || rule.language === languageFilter.value
    const matchesSeverity = severityFilter.value === 'All' || rule.severity === severityFilter.value
    const matchesCategory = categoryFilter.value === 'All' || rule.category === categoryFilter.value
    const matchesKeyword = keyword.length === 0
      || [rule.id, rule.cwe, rule.language].some((value) => value.toLocaleLowerCase().includes(keyword))

    return matchesLanguage && matchesSeverity && matchesCategory && matchesKeyword
  })
})

function resetFilters(): void {
  languageFilter.value = 'All'
  severityFilter.value = 'All'
  categoryFilter.value = 'All'
  query.value = ''
}

function openDetails(rule: RuleRecord): void {
  selectedRule.value = rule
}

function closeDetails(): void {
  selectedRule.value = null
}
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
        <span class="state-dot" aria-hidden="true"></span>
        <div>
          <span>规则来源</span>
          <strong>rules/*.yaml</strong>
        </div>
      </div>
    </header>

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
              <td><SeverityBadge :severity="rule.severity" /></td>
              <td class="rule-id">{{ rule.id }}</td>
              <td><span class="language-tag">{{ rule.language }}</span></td>
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
}
</style>
