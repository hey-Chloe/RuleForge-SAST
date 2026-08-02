<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  fetchScanHistory,
  readableHistoryApiError,
  type ScanHistoryRecord,
} from '../services/historyApi'

const records = ref<ScanHistoryRecord[]>([])
const loading = ref(true)
const error = ref('')
const query = ref('')

const stats = computed(() => {
  const totalScans = records.value.length
  const totalFindings = records.value.reduce((sum, record) => sum + record.finding_count, 0)
  const languages = new Set(records.value.map((record) => record.language)).size
  const totalRules = records.value.reduce((sum, record) => sum + record.rule_count, 0)
  return [
    {
      label: 'Total Scans',
      value: totalScans,
      helper: '真实扫描历史记录',
      tone: 'total',
    },
    {
      label: 'Findings',
      value: totalFindings,
      helper: '累计漏洞数量',
      tone: 'findings',
    },
    {
      label: 'Languages',
      value: languages,
      helper: '覆盖语言种类',
      tone: 'markdown',
    },
    {
      label: 'Rules Used',
      value: totalRules,
      helper: '累计使用规则次数',
      tone: 'json',
    },
  ]
})

const filteredRecords = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()
  if (keyword.length === 0) {
    return records.value
  }
  return records.value.filter((record) =>
    [record.filename, record.language, record.rule_id ?? ''].some((value) =>
      value.toLocaleLowerCase().includes(keyword),
    ),
  )
})

function resetFilters(): void {
  query.value = ''
}

async function loadHistory(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const response = await fetchScanHistory()
    records.value = response.history
  } catch (err) {
    error.value = readableHistoryApiError(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>

<template>
  <section class="reports-view" aria-labelledby="reports-title">
    <header class="view-intro">
      <div>
        <span class="view-eyebrow">Scan history center</span>
        <h1 id="reports-title">扫描历史中心</h1>
        <p>浏览后端保存的真实扫描历史记录。</p>
      </div>
      <div class="preview-state">
        <span class="state-dot" aria-hidden="true"></span>
        <div>
          <span>数据模式</span>
          <strong>Real History</strong>
        </div>
      </div>
    </header>

    <div class="stats-grid" aria-label="扫描历史统计">
      <article v-for="stat in stats" :key="stat.label" class="stat-card" :class="`tone-${stat.tone}`">
        <div>
          <span>{{ stat.label }}</span>
          <i aria-hidden="true"></i>
        </div>
        <strong>{{ stat.value }}</strong>
        <p>{{ stat.helper }}</p>
      </article>
    </div>

    <section class="filters-card" aria-label="扫描历史筛选">
      <div class="filter-field search-field">
        <label for="history-search">关键词搜索</label>
        <div class="search-control">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m16 16 4 4" />
          </svg>
          <input
            id="history-search"
            v-model="query"
            type="search"
            placeholder="文件名、语言或规则"
          >
        </div>
      </div>
      <div class="filter-summary">
        <span>{{ filteredRecords.length }} records</span>
        <button type="button" @click="resetFilters">重置筛选</button>
      </div>
    </section>

    <section class="reports-table-card" aria-label="扫描历史列表">
      <div class="table-heading">
        <div>
          <span class="section-kicker">Real scan history</span>
          <h2>扫描历史记录</h2>
        </div>
        <span>按时间倒序排列</span>
      </div>

      <div v-if="loading" class="state-block">
        <strong>正在加载扫描历史…</strong>
        <p>正在从后端读取真实扫描记录。</p>
      </div>

      <div v-else-if="error" class="state-block error-state">
        <strong>无法加载扫描历史</strong>
        <p>{{ error }}</p>
        <button type="button" @click="loadHistory">重试</button>
      </div>

      <div v-else-if="filteredRecords.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>文件名</th>
              <th>语言</th>
              <th>扫描模式</th>
              <th>使用规则</th>
              <th>漏洞数量</th>
              <th>状态</th>
              <th>扫描时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredRecords" :key="record.id">
              <td class="report-name">{{ record.filename }}</td>
              <td><span class="lang-tag">{{ record.language }}</span></td>
              <td class="mode-cell">{{ record.scan_mode }}</td>
              <td class="rule-cell">
                <span v-if="record.rule_id">{{ record.rule_id }}</span>
                <span v-else class="muted">全部规则（{{ record.rule_count }}）</span>
              </td>
              <td class="finding-count">{{ record.finding_count }}</td>
              <td><span class="status-tag" :class="`status-${record.status.toLowerCase()}`">{{ record.status }}</span></td>
              <td class="generated-at">{{ record.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-state">
        <strong>没有扫描历史记录</strong>
        <p>完成一次扫描后，记录会显示在这里。</p>
        <button v-if="query" type="button" @click="resetFilters">清除筛选</button>
      </div>
    </section>
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
  background: #3f725c;
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
  color: #3f725c;
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

.filters-card {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  align-items: end;
  gap: 13px;
  padding: 18px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.filter-field {
  display: grid;
  gap: 7px;
}

label {
  color: #68798d;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: .05em;
  text-transform: uppercase;
}

input {
  width: 100%;
  height: 40px;
  color: #33485f;
  background: #fbfcfd;
  border: 1px solid #dbe3eb;
  border-radius: 8px;
  outline: none;
  padding: 0 12px 0 36px;
}

input:focus {
  border-color: #8ea5bd;
  box-shadow: 0 0 0 3px #eef3f7;
}

input::placeholder {
  color: #9aa6b4;
}

.search-control {
  position: relative;
}

.search-control svg {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 16px;
  fill: none;
  stroke: #8493a4;
  stroke-linecap: round;
  stroke-width: 1.7;
}

.filter-summary {
  display: flex;
  min-height: 40px;
  align-items: center;
  justify-content: flex-end;
  gap: 11px;
  white-space: nowrap;
}

.filter-summary span {
  color: #748397;
  font-size: 11px;
}

.filter-summary button {
  padding: 8px 10px;
  color: #526d8a;
  background: #edf2f7;
  border: 1px solid #dce5ed;
  border-radius: 7px;
  cursor: pointer;
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
  min-width: 900px;
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

tbody tr:hover {
  background: #f7fafc;
}

.report-name {
  color: #385470;
  font-weight: 700;
}

.generated-at {
  color: #64768a;
  font-family: var(--mono-font);
}

.lang-tag,
.status-tag {
  display: inline-flex;
  padding: 4px 7px;
  font-size: 9px;
  font-weight: 750;
  border-radius: 5px;
}

.lang-tag {
  color: #4f6b88;
  background: #eaf0f5;
}

.status-success {
  color: #3f725c;
  background: #e5f0eb;
}

.status-failed {
  color: #a83b46;
  background: #f6e7e9;
}

.mode-cell {
  font-family: var(--mono-font);
  color: #64768a;
}

.rule-cell {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--mono-font);
  color: #64768a;
}

.rule-cell .muted {
  color: #9aa6b4;
}

.finding-count {
  color: var(--heading-color);
  font-weight: 750;
}

.state-block {
  display: grid;
  justify-items: center;
  padding: 56px 20px;
  text-align: center;
  border-top: 1px solid #edf0f4;
}

.state-block strong {
  color: #40566d;
  font-size: 13px;
}

.state-block p {
  margin: 7px 0 15px;
  color: #8190a1;
  font-size: 11px;
}

.state-block button {
  padding: 8px 11px;
  color: #526d8a;
  background: #edf2f7;
  border: 1px solid #dce5ed;
  border-radius: 7px;
  cursor: pointer;
}

.error-state strong {
  color: #a83b46;
}

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

  .filters-card {
    grid-template-columns: 1fr;
  }

  .filter-summary {
    justify-content: space-between;
  }
}

@media (max-width: 430px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
