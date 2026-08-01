<script setup lang="ts">
import SeverityBadge from './SeverityBadge.vue'
import type { VulnerabilityRecord } from '../types/dashboard'

defineProps<{
  findings: VulnerabilityRecord[]
}>()

const emit = defineEmits<{
  select: [finding: VulnerabilityRecord]
}>()
</script>

<template>
  <div class="scan-table-wrap">
    <table>
      <thead>
        <tr>
          <th>Severity</th>
          <th>Rule ID</th>
          <th>CWE</th>
          <th>Category</th>
          <th>File</th>
          <th>Line</th>
          <th>Description</th>
          <th>修复建议</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="finding in findings" :key="finding.id">
          <td><SeverityBadge :severity="finding.severity" /></td>
          <td class="rule-id">{{ finding.ruleId }}</td>
          <td class="mono muted">{{ finding.cwe }}</td>
          <td>{{ finding.category }}</td>
          <td class="file-path" :title="finding.file">{{ finding.file }}</td>
          <td class="mono">{{ finding.line }}</td>
          <td class="description" :title="finding.description">{{ finding.description }}</td>
          <td>
            <button type="button" @click="emit('select', finding)">查看详情</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.scan-table-wrap {
  overflow-x: auto;
  border-top: 1px solid #edf0f4;
}

table {
  width: 100%;
  min-width: 1060px;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #edf0f4;
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

tbody tr:last-child td {
  border-bottom: 0;
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

.file-path,
.description {
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

button {
  padding: 7px 10px;
  color: #496883;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
  background: #edf3f7;
  border: 1px solid #d8e3eb;
  border-radius: 6px;
  cursor: pointer;
}
</style>
