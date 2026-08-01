<script setup lang="ts">
import type { DashboardMetric } from '../types/dashboard'

defineProps<{
  metric: DashboardMetric
}>()
</script>

<template>
  <article class="stat-card" :class="`tone-${metric.tone}`">
    <div class="stat-header">
      <span>{{ metric.label }}</span>
      <span class="metric-mark" aria-hidden="true"></span>
    </div>
    <strong class="stat-value">{{ metric.value }}</strong>
    <p>{{ metric.helper }}</p>
  </article>
</template>

<style scoped>
.stat-card {
  min-width: 0;
  padding: 20px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #607186;
  font-size: 12px;
  font-weight: 650;
}

.metric-mark {
  width: 9px;
  height: 9px;
  background: #7189a5;
  border-radius: 3px;
}

.stat-value {
  display: block;
  margin-top: 16px;
  color: var(--heading-color);
  font-size: clamp(28px, 3vw, 36px);
  line-height: 1;
  letter-spacing: -.04em;
}

.stat-card p {
  margin: 10px 0 0;
  color: var(--muted-text);
  font-size: 11px;
}

.tone-critical .metric-mark { background: var(--critical-color); }
.tone-high .metric-mark { background: var(--high-color); }
.tone-primary .metric-mark { background: var(--primary-color); }
.tone-critical .stat-value { color: #b33e47; }
.tone-high .stat-value { color: #b96831; }
</style>

