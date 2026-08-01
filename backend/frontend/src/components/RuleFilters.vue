<script setup lang="ts">
import type { RuleLanguageFilter, RuleSeverityFilter } from '../types/rules'

defineProps<{
  language: RuleLanguageFilter
  severity: RuleSeverityFilter
  category: string
  query: string
  categories: string[]
  resultCount: number
}>()

const emit = defineEmits<{
  'update:language': [value: RuleLanguageFilter]
  'update:severity': [value: RuleSeverityFilter]
  'update:category': [value: string]
  'update:query': [value: string]
  reset: []
}>()

const languageOptions: RuleLanguageFilter[] = ['All', 'PHP', 'Python', 'Java', 'Generic']
const severityOptions: RuleSeverityFilter[] = ['All', 'Critical', 'High', 'Medium']

function updateLanguage(event: Event): void {
  emit('update:language', (event.target as HTMLSelectElement).value as RuleLanguageFilter)
}

function updateSeverity(event: Event): void {
  emit('update:severity', (event.target as HTMLSelectElement).value as RuleSeverityFilter)
}

function updateCategory(event: Event): void {
  emit('update:category', (event.target as HTMLSelectElement).value)
}

function updateQuery(event: Event): void {
  emit('update:query', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <section class="filters-card" aria-label="规则筛选">
    <div class="filter-field search-field">
      <label for="rule-search">关键词搜索</label>
      <div class="search-control">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="m16 16 4 4" />
        </svg>
        <input
          id="rule-search"
          :value="query"
          type="search"
          placeholder="Rule ID、CWE 或 Language"
          @input="updateQuery"
        >
      </div>
    </div>

    <div class="filter-field">
      <label for="rule-language">Language</label>
      <select id="rule-language" :value="language" @change="updateLanguage">
        <option v-for="option in languageOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="filter-field">
      <label for="rule-severity">Severity</label>
      <select id="rule-severity" :value="severity" @change="updateSeverity">
        <option v-for="option in severityOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="filter-field">
      <label for="rule-category">Category</label>
      <select id="rule-category" :value="category" @change="updateCategory">
        <option value="All">All</option>
        <option v-for="option in categories" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="filter-summary">
      <span>{{ resultCount }} rules</span>
      <button type="button" @click="emit('reset')">重置筛选</button>
    </div>
  </section>
</template>

<style scoped>
.filters-card {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 140px 140px 180px auto;
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

@media (max-width: 1240px) {
  .filters-card {
    grid-template-columns: minmax(240px, 1fr) repeat(3, minmax(130px, .45fr));
  }

  .filter-summary {
    grid-column: 1 / -1;
  }
}

@media (max-width: 760px) {
  .filters-card {
    grid-template-columns: repeat(3, 1fr);
  }

  .search-field {
    grid-column: 1 / -1;
  }
}

@media (max-width: 560px) {
  .filters-card {
    grid-template-columns: 1fr;
  }

  .search-field,
  .filter-summary {
    grid-column: auto;
  }

  .filter-summary {
    justify-content: space-between;
  }
}
</style>
