<script setup lang="ts">
import SeverityBadge from './SeverityBadge.vue'
import type { FindingStatus, RecentFinding } from '../types/dashboard'

defineProps<{
  findings: RecentFinding[]
}>()

const statusLabels: Record<FindingStatus, string> = {
  Open: '待修复',
  Reviewing: '复核中',
  Fixed: '已修复',
}
</script>

<template>
  <section class="findings-card">
    <div class="card-heading">
      <div>
        <span class="section-kicker">最近发现</span>
        <h2>Recent Findings</h2>
        <p>按风险优先级排列的最新代码安全问题</p>
      </div>
      <span class="finding-count">{{ findings.length }} findings</span>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Severity</th>
            <th>Rule ID</th>
            <th>CWE</th>
            <th>File</th>
            <th>Line</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="finding in findings" :key="`${finding.ruleId}-${finding.file}-${finding.line}`">
            <td><SeverityBadge :severity="finding.severity" /></td>
            <td class="rule-id">{{ finding.ruleId }}</td>
            <td class="mono muted">{{ finding.cwe }}</td>
            <td class="file-path" :title="finding.file">{{ finding.file }}</td>
            <td class="mono">{{ finding.line }}</td>
            <td><span class="status" :class="`status-${finding.status.toLowerCase()}`">{{ statusLabels[finding.status] }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.findings-card {
  min-width: 0;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.card-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 22px 22px 18px;
}

.section-kicker {
  color: var(--primary-color);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

h2 {
  margin: 5px 0 0;
  color: var(--heading-color);
  font-size: 16px;
}

p {
  margin: 6px 0 0;
  color: var(--muted-text);
  font-size: 11px;
}

.finding-count {
  padding: 5px 8px;
  color: #60758c;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  background: #f1f5f8;
  border-radius: 5px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 820px;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 18px;
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
  color: #3e5065;
  font-size: 11px;
}

tbody tr:hover {
  background: #fbfcfd;
}

.rule-id,
.mono,
.file-path {
  font-family: var(--mono-font);
}

.rule-id {
  color: #354f6a;
  font-weight: 650;
}

.file-path {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.muted {
  color: #718196;
}

.status {
  display: inline-flex;
  padding: 5px 9px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 6px;
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

@media (max-width: 640px) {
  .card-heading {
    padding-inline: 16px;
  }
}
</style>

