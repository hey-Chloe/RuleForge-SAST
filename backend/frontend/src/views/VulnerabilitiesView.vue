<script setup lang="ts">
import { computed, ref } from 'vue'
import SeverityBadge from '../components/SeverityBadge.vue'
import VulnerabilityDetailPanel from '../components/VulnerabilityDetailPanel.vue'
import VulnerabilityFilters from '../components/VulnerabilityFilters.vue'
import { vulnerabilities } from '../data/dashboardMock'
import type {
  FindingStatus,
  LanguageFilter,
  SeverityFilter,
  VulnerabilityRecord,
} from '../types/dashboard'

const severityFilter = ref<SeverityFilter>('All')
const languageFilter = ref<LanguageFilter>('All')
const query = ref('')
const selectedVulnerability = ref<VulnerabilityRecord | null>(null)

const statusLabels: Record<FindingStatus, string> = {
  Open: '待修复',
  Reviewing: '复核中',
  Fixed: '已修复',
}

const filteredVulnerabilities = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()

  return vulnerabilities.filter((vulnerability) => {
    const matchesSeverity = severityFilter.value === 'All'
      || vulnerability.severity === severityFilter.value
    const matchesLanguage = languageFilter.value === 'All'
      || vulnerability.language === languageFilter.value
    const matchesKeyword = keyword.length === 0
      || [vulnerability.ruleId, vulnerability.cwe, vulnerability.file]
        .some((value) => value.toLocaleLowerCase().includes(keyword))

    return matchesSeverity && matchesLanguage && matchesKeyword
  })
})

function resetFilters(): void {
  severityFilter.value = 'All'
  languageFilter.value = 'All'
  query.value = ''
}

function openDetails(vulnerability: VulnerabilityRecord): void {
  selectedVulnerability.value = vulnerability
}

function closeDetails(): void {
  selectedVulnerability.value = null
}
</script>

<template>
  <section class="vulnerabilities-view" aria-labelledby="vulnerabilities-title">
    <header class="view-intro">
      <div>
        <span class="view-eyebrow">Findings workspace</span>
        <h1 id="vulnerabilities-title">漏洞管理</h1>
        <p>查看扫描发现，按风险和语言筛选，并获取修复与 Patch 验证信息。</p>
      </div>
      <div class="finding-summary">
        <span>当前项目</span>
        <strong>{{ vulnerabilities.length }} 个漏洞发现</strong>
      </div>
    </header>

    <VulnerabilityFilters
      :severity="severityFilter"
      :language="languageFilter"
      :query="query"
      :result-count="filteredVulnerabilities.length"
      @update:severity="severityFilter = $event"
      @update:language="languageFilter = $event"
      @update:query="query = $event"
      @reset="resetFilters"
    />

    <section class="vulnerability-table-card" aria-label="漏洞列表">
      <div class="table-heading">
        <div>
          <span class="section-kicker">Vulnerabilities</span>
          <h2>扫描发现</h2>
        </div>
        <span>点击列表项查看详情</span>
      </div>

      <div v-if="filteredVulnerabilities.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Rule ID</th>
              <th>CWE</th>
              <th>Category</th>
              <th>Language</th>
              <th>File</th>
              <th>Line</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="vulnerability in filteredVulnerabilities"
              :key="vulnerability.id"
              tabindex="0"
              @click="openDetails(vulnerability)"
              @keydown.enter="openDetails(vulnerability)"
            >
              <td><SeverityBadge :severity="vulnerability.severity" /></td>
              <td class="rule-id">{{ vulnerability.ruleId }}</td>
              <td class="mono muted">{{ vulnerability.cwe }}</td>
              <td>{{ vulnerability.category }}</td>
              <td><span class="language-tag">{{ vulnerability.language }}</span></td>
              <td class="file-path" :title="vulnerability.file">{{ vulnerability.file }}</td>
              <td class="mono">{{ vulnerability.line }}</td>
              <td>
                <span class="status" :class="`status-${vulnerability.status.toLowerCase()}`">
                  {{ statusLabels[vulnerability.status] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-state">
        <strong>没有匹配的漏洞</strong>
        <p>调整筛选条件或清除关键词后重试。</p>
        <button type="button" @click="resetFilters">清除筛选</button>
      </div>
    </section>

    <VulnerabilityDetailPanel
      v-if="selectedVulnerability"
      :vulnerability="selectedVulnerability"
      @close="closeDetails"
    />
  </section>
</template>

<style scoped>
.vulnerabilities-view {
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

.finding-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.finding-summary span {
  color: var(--muted-text);
  font-size: 10px;
}

.finding-summary strong {
  color: #3c536b;
  font-size: 12px;
}

.vulnerability-table-card {
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
  min-width: 1080px;
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
.mono,
.file-path {
  font-family: var(--mono-font);
}

.rule-id {
  color: #385470;
  font-weight: 650;
}

.muted {
  color: #718196;
}

.file-path {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.language-tag {
  padding: 4px 7px;
  color: #536b84;
  font-size: 10px;
  font-weight: 700;
  background: #edf2f6;
  border-radius: 5px;
}

.status {
  display: inline-flex;
  padding: 5px 8px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 6px;
  white-space: nowrap;
}

.status-open {
  color: #9d4047;
  background: #faecee;
}

.status-reviewing {
  color: #896d24;
  background: #f9f3dd;
}

.status-fixed {
  color: #42735f;
  background: #eaf3ef;
}

.empty-state {
  display: grid;
  min-height: 260px;
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

@media (max-width: 640px) {
  .vulnerabilities-view {
    padding: 20px 16px 28px;
  }

  .view-intro {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 22px;
  }

  .finding-summary {
    align-items: flex-start;
  }

  .table-heading {
    padding-inline: 16px;
  }
}
</style>
