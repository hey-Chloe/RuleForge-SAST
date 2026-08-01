<script setup lang="ts">
import type { ReportFormatFilter, ReportStatusFilter } from '../types/reports'

defineProps<{
  format: ReportFormatFilter
  status: ReportStatusFilter
  query: string
  resultCount: number
}>()

const emit = defineEmits<{
  'update:format': [value: ReportFormatFilter]
  'update:status': [value: ReportStatusFilter]
  'update:query': [value: string]
  reset: []
}>()

const formatOptions: ReportFormatFilter[] = ['All', 'Markdown', 'JSON']
const statusOptions: ReportStatusFilter[] = ['All', 'Ready', 'Draft']

function updateFormat(event: Event): void {
  emit('update:format', (event.target as HTMLSelectElement).value as ReportFormatFilter)
}

function updateStatus(event: Event): void {
  emit('update:status', (event.target as HTMLSelectElement).value as ReportStatusFilter)
}

function updateQuery(event: Event): void {
  emit('update:query', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <section class="filters-card" aria-label="报告筛选">
    <div class="filter-field search-field">
      <label for="report-search">关键词搜索</label>
      <div class="search-control">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="m16 16 4 4" />
        </svg>
        <input
          id="report-search"
          :value="query"
          type="search"
          placeholder="报告名称或扫描目标"
          @input="updateQuery"
        >
      </div>
    </div>

    <div class="filter-field">
      <label for="report-format">Format</label>
      <select id="report-format" :value="format" @change="updateFormat">
        <option v-for="option in formatOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="filter-field">
      <label for="report-status">Status</label>
      <select id="report-status" :value="status" @change="updateStatus">
        <option v-for="option in statusOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="filter-summary">
      <span>{{ resultCount }} reports</span>
      <button type="button" @click="emit('reset')">重置筛选</button>
    </div>
  </section>
</template>

<style scoped>
.filters-card {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 170px 170px auto;
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

select,
input {
  width: 100%;
  height: 40px;
  color: #33485f;
  background: #fbfcfd;
  border: 1px solid #dbe3eb;
  border-radius: 8px;
  outline: none;
}

select {
  padding: 0 30px 0 10px;
}

input {
  padding: 0 12px 0 36px;
}

select:focus,
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

@media (max-width: 900px) {
  .filters-card {
    grid-template-columns: minmax(230px, 1fr) repeat(2, 150px);
  }

  .filter-summary {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .filters-card {
    grid-template-columns: 1fr 1fr;
  }

  .search-field,
  .filter-summary {
    grid-column: 1 / -1;
  }

  .filter-summary {
    justify-content: space-between;
  }
}

@media (max-width: 420px) {
  .filters-card {
    grid-template-columns: 1fr;
  }

  .search-field,
  .filter-summary {
    grid-column: auto;
  }
}
</style>
