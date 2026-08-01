<script setup lang="ts">
import { computed, ref } from 'vue'
import ReportFilters from '../components/ReportFilters.vue'
import ReportPreviewPanel from '../components/ReportPreviewPanel.vue'
import { reportsMock } from '../data/reportsMock'
import type { ReportFormatFilter, ReportRecord, ReportStatusFilter } from '../types/reports'

const formatFilter = ref<ReportFormatFilter>('All')
const statusFilter = ref<ReportStatusFilter>('All')
const query = ref('')
const selectedReport = ref<ReportRecord | null>(null)

const stats = [
  {
    label: 'Local Reports',
    value: reportsMock.length,
    helper: '全部为 Demo Data',
    tone: 'total',
  },
  {
    label: 'Markdown',
    value: reportsMock.filter((report) => report.format === 'Markdown').length,
    helper: '本地 Markdown 预览',
    tone: 'markdown',
  },
  {
    label: 'JSON',
    value: reportsMock.filter((report) => report.format === 'JSON').length,
    helper: '兼容扫描结果结构',
    tone: 'json',
  },
  {
    label: 'Demo Findings',
    value: reportsMock.reduce((total, report) => total + report.findings, 0),
    helper: '非真实扫描历史',
    tone: 'findings',
  },
]

const filteredReports = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()

  return reportsMock.filter((report) => {
    const matchesFormat = formatFilter.value === 'All' || report.format === formatFilter.value
    const matchesStatus = statusFilter.value === 'All' || report.status === statusFilter.value
    const matchesKeyword = keyword.length === 0
      || [report.name, report.scanTarget].some((value) => value.toLocaleLowerCase().includes(keyword))

    return matchesFormat && matchesStatus && matchesKeyword
  })
})

function resetFilters(): void {
  formatFilter.value = 'All'
  statusFilter.value = 'All'
  query.value = ''
}

function openPreview(report: ReportRecord): void {
  selectedReport.value = report
}

function closePreview(): void {
  selectedReport.value = null
}
</script>

<template>
  <section class="reports-view" aria-labelledby="reports-title">
    <header class="view-intro">
      <div>
        <span class="view-eyebrow">Local report center</span>
        <h1 id="reports-title">安全报告中心</h1>
        <p>浏览本地示例报告，并预览或导出 Markdown 与 JSON 文件。</p>
      </div>
      <div class="preview-state">
        <span class="state-dot" aria-hidden="true"></span>
        <div>
          <span>数据模式</span>
          <strong>Demo Data</strong>
        </div>
      </div>
    </header>

    <aside class="scope-notice" aria-label="报告中心数据说明">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 10v6m0-9h.01" />
      </svg>
      <div>
        <strong>当前页面是 Local Preview，仅使用前端 Demo Data。</strong>
        <p>后端尚未提供报告历史、持久化或下载 API；下载文件由浏览器根据当前示例数据即时生成。</p>
      </div>
    </aside>

    <div class="stats-grid" aria-label="本地报告统计">
      <article v-for="stat in stats" :key="stat.label" class="stat-card" :class="`tone-${stat.tone}`">
        <div>
          <span>{{ stat.label }}</span>
          <i aria-hidden="true"></i>
        </div>
        <strong>{{ stat.value }}</strong>
        <p>{{ stat.helper }}</p>
      </article>
    </div>

    <ReportFilters
      :format="formatFilter"
      :status="statusFilter"
      :query="query"
      :result-count="filteredReports.length"
      @update:format="formatFilter = $event"
      @update:status="statusFilter = $event"
      @update:query="query = $event"
      @reset="resetFilters"
    />

    <section class="reports-table-card" aria-label="本地报告列表">
      <div class="table-heading">
        <div>
          <span class="section-kicker">Demo report history</span>
          <h2>本地报告记录</h2>
        </div>
        <span>点击报告查看 Local Preview</span>
      </div>

      <div v-if="filteredReports.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Report Name</th>
              <th>Scan Target</th>
              <th>Format</th>
              <th>Findings</th>
              <th>Critical / High</th>
              <th>Generated At</th>
              <th>Status</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="report in filteredReports"
              :key="report.id"
              tabindex="0"
              @click="openPreview(report)"
              @keydown.enter="openPreview(report)"
            >
              <td class="report-name">{{ report.name }}</td>
              <td class="target">{{ report.scanTarget }}</td>
              <td><span class="format-tag" :class="`format-${report.format.toLowerCase()}`">{{ report.format }}</span></td>
              <td class="finding-count">{{ report.findings }}</td>
              <td>
                <div class="risk-counts">
                  <span class="critical-count">{{ report.critical }}</span>
                  <span aria-hidden="true">/</span>
                  <span class="high-count">{{ report.high }}</span>
                </div>
              </td>
              <td class="generated-at">{{ report.generatedAt }}</td>
              <td><span class="status-tag" :class="`status-${report.status.toLowerCase()}`">{{ report.status }}</span></td>
              <td><span class="demo-tag">{{ report.sourceLabel }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-state">
        <strong>没有匹配的本地报告</strong>
        <p>调整格式、状态或关键词条件后重试。</p>
        <button type="button" @click="resetFilters">清除筛选</button>
      </div>
    </section>

    <ReportPreviewPanel v-if="selectedReport" :report="selectedReport" @close="closePreview" />
  </section>
</template>

<style scoped>
.reports-view {
  width: min(100%, 1520px);
  margin: 0 auto;
  padding: clamp(24px, 3vw, 40px);
}

.view-intro {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 22px;
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

.preview-state {
  display: flex;
  align-items: center;
  gap: 10px;
}

.state-dot {
  width: 9px;
  height: 9px;
  background: #b59747;
  border-radius: 50%;
}

.preview-state div {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}

.preview-state span {
  color: var(--muted-text);
  font-size: 10px;
}

.preview-state strong {
  color: #725f2a;
  font-family: var(--mono-font);
  font-size: 11px;
}

.scope-notice {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  margin-bottom: 18px;
  padding: 16px 18px;
  background: #f8f4e7;
  border: 1px solid #e9dfbd;
  border-radius: 10px;
}

.scope-notice svg {
  width: 19px;
  flex: 0 0 19px;
  fill: none;
  stroke: #8b773c;
  stroke-linecap: round;
  stroke-width: 1.6;
}

.scope-notice strong {
  color: #6e5c29;
  font-size: 12px;
}

.scope-notice p {
  margin: 5px 0 0;
  color: #7d7353;
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

.tone-markdown i { background: #7189a5; }
.tone-json i { background: #73927f; }
.tone-findings i { background: #b77850; }

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

.reports-table-card {
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
  min-width: 1120px;
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

.report-name {
  color: #385470;
  font-weight: 700;
}

.target,
.generated-at {
  color: #64768a;
  font-family: var(--mono-font);
}

.target {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.format-tag,
.status-tag,
.demo-tag {
  display: inline-flex;
  padding: 4px 7px;
  font-size: 9px;
  font-weight: 750;
  border-radius: 5px;
}

.format-markdown {
  color: #4f6b88;
  background: #eaf0f5;
}

.format-json {
  color: #4c7564;
  background: #e8f1ed;
}

.status-ready {
  color: #3f725c;
  background: #e5f0eb;
}

.status-draft {
  color: #846b20;
  background: #f8f1d9;
}

.demo-tag {
  color: #6d6031;
  background: #f8f1d9;
  border: 1px solid #eadca9;
}

.finding-count {
  color: var(--heading-color);
  font-weight: 750;
}

.risk-counts {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--mono-font);
  font-weight: 750;
}

.critical-count { color: #a83b46; }
.high-count { color: #ad612f; }

.empty-state {
  display: grid;
  justify-items: center;
  padding: 56px 20px;
  text-align: center;
  border-top: 1px solid #edf0f4;
}

.empty-state strong {
  color: #40566d;
  font-size: 13px;
}

.empty-state p {
  margin: 7px 0 15px;
  color: #8190a1;
  font-size: 11px;
}

.empty-state button {
  padding: 8px 11px;
  color: #526d8a;
  background: #edf2f7;
  border: 1px solid #dce5ed;
  border-radius: 7px;
  cursor: pointer;
}

@media (max-width: 980px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .reports-view {
    padding: 20px 16px 28px;
  }

  .view-intro {
    align-items: flex-start;
    flex-direction: column;
  }

  .preview-state div {
    align-items: flex-start;
  }

  .table-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 430px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
