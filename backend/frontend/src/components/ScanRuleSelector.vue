<script setup lang="ts">
import { computed } from 'vue'
import type { RuleCatalogItem, RuleCatalogState } from '../types/rules'

const props = defineProps<{
  state: RuleCatalogState
  rules: RuleCatalogItem[]
  selectedRuleId: string
  errorMessage: string
  disabled: boolean
}>()

const emit = defineEmits<{
  'update:selectedRuleId': [value: string]
  retry: []
}>()

const selectedRule = computed(() => (
  props.rules.find((rule) => rule.id === props.selectedRuleId) ?? null
))

function updateRule(event: Event): void {
  emit('update:selectedRuleId', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <section class="rule-selector" aria-labelledby="scan-rule-title">
    <div class="selector-heading">
      <div>
        <span>Scan rule</span>
        <h2 id="scan-rule-title">选择 PHP 安全规则</h2>
      </div>
      <code>GET /rules</code>
    </div>

    <div v-if="state === 'Loading'" class="selector-state" role="status" aria-live="polite">
      <span class="loading-dot" aria-hidden="true"></span>
      <p>正在读取本地 PHP 规则...</p>
    </div>

    <div v-else-if="state === 'Failed'" class="selector-state selector-failed" role="alert">
      <div>
        <strong>无法连接本地规则库 API</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button type="button" @click="emit('retry')">Retry</button>
    </div>

    <div v-else-if="state === 'Empty'" class="selector-state selector-empty">
      <div>
        <strong>没有可用的 PHP 规则</strong>
        <p>规则 API 已响应，但未返回 languages 包含 php 的规则。</p>
      </div>
      <button type="button" @click="emit('retry')">重新加载</button>
    </div>

    <template v-else>
      <label for="scan-rule">Rule ID · Severity · CWE</label>
      <select id="scan-rule" :value="selectedRuleId" :disabled="disabled" @change="updateRule">
        <option v-for="rule in rules" :key="rule.id" :value="rule.id">
          {{ rule.id }} · {{ rule.severity }} · {{ rule.cwe }}
        </option>
      </select>

      <div v-if="selectedRule" class="selected-rule" aria-live="polite">
        <div>
          <span>本次选择</span>
          <strong>{{ selectedRule.id }}</strong>
        </div>
        <dl>
          <div>
            <dt>Severity</dt>
            <dd>{{ selectedRule.severity }}</dd>
          </div>
          <div>
            <dt>CWE</dt>
            <dd>{{ selectedRule.cwe }}</dd>
          </div>
          <div>
            <dt>Category</dt>
            <dd>{{ selectedRule.category }}</dd>
          </div>
        </dl>
      </div>
    </template>
  </section>
</template>

<style scoped>
.rule-selector {
  display: grid;
  gap: 13px;
  padding: 20px 22px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.selector-heading,
.selector-state,
.selected-rule,
.selected-rule dl {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.selector-heading span {
  color: var(--primary-color);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

.selector-heading h2 {
  margin: 5px 0 0;
  color: var(--heading-color);
  font-size: 16px;
}

.selector-heading code {
  padding: 6px 9px;
  color: #4d6279;
  font-family: var(--mono-font);
  font-size: 10px;
  background: #f1f5f8;
  border-radius: 6px;
}

label,
.selected-rule span,
dt {
  color: #748397;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .06em;
  text-transform: uppercase;
}

select {
  width: 100%;
  height: 42px;
  padding: 0 12px;
  color: #33485f;
  font-family: var(--mono-font);
  font-size: 11px;
  background: #fbfcfd;
  border: 1px solid #d7e0e8;
  border-radius: 8px;
  outline: none;
}

select:focus {
  border-color: #8ea5bd;
  box-shadow: 0 0 0 3px #eef3f7;
}

select:disabled {
  color: #8794a2;
  background: #eef2f5;
}

.selected-rule {
  align-items: flex-start;
  padding: 14px 15px;
  background: #f5f8fa;
  border: 1px solid #e1e8ee;
  border-radius: 8px;
}

.selected-rule > div {
  display: grid;
  gap: 5px;
}

.selected-rule strong {
  color: #385470;
  font-family: var(--mono-font);
  font-size: 11px;
}

.selected-rule dl {
  align-items: flex-start;
  margin: 0;
}

.selected-rule dl div {
  min-width: 75px;
}

dd {
  margin: 4px 0 0;
  color: #4d6279;
  font-family: var(--mono-font);
  font-size: 10px;
}

.selector-state {
  min-height: 86px;
  justify-content: flex-start;
  padding: 14px 16px;
  color: #66788c;
  background: #f7f9fb;
  border: 1px solid #e1e7ed;
  border-radius: 8px;
}

.selector-state p {
  margin: 0;
  font-size: 11px;
  line-height: 1.6;
}

.selector-state strong {
  color: #8d3941;
  font-size: 12px;
}

.selector-state div p {
  margin-top: 5px;
}

.selector-state button {
  margin-left: auto;
  padding: 8px 12px;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  background: #526f8e;
  border: 1px solid #486784;
  border-radius: 7px;
  cursor: pointer;
}

.selector-failed {
  background: #fffafb;
  border-color: #eccfd3;
}

.loading-dot {
  width: 9px;
  height: 9px;
  flex: 0 0 9px;
  background: #6f89a6;
  border-radius: 50%;
}

@media (max-width: 700px) {
  .selected-rule,
  .selector-state {
    align-items: flex-start;
    flex-direction: column;
  }

  .selected-rule dl {
    width: 100%;
    flex-wrap: wrap;
  }

  .selector-state button {
    margin-left: 0;
  }
}
</style>
