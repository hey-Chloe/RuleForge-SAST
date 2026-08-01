<script setup lang="ts">
import { computed } from 'vue'
import type { DistributionItem } from '../types/dashboard'

const props = defineProps<{
  items: DistributionItem[]
}>()

const radius = 44
const circumference = 2 * Math.PI * radius

const total = computed(() => props.items.reduce((sum, item) => sum + item.value, 0))

const segments = computed(() => {
  let offset = 0
  return props.items.map((item) => {
    const length = total.value === 0 ? 0 : (item.value / total.value) * circumference
    const segment = {
      ...item,
      dasharray: `${length} ${circumference - length}`,
      dashoffset: -offset,
      percentage: total.value === 0 ? 0 : Math.round((item.value / total.value) * 100),
    }
    offset += length
    return segment
  })
})
</script>

<template>
  <section class="distribution-card">
    <span class="section-kicker">分类</span>
    <h2>Vulnerability Distribution</h2>
    <p class="description">按漏洞类型汇总当前发现</p>

    <div class="distribution-body">
      <div class="donut-wrap" aria-label="漏洞类型分布环形图" role="img">
        <svg viewBox="0 0 120 120">
          <circle class="donut-track" cx="60" cy="60" :r="radius" />
          <circle
            v-for="segment in segments"
            :key="segment.label"
            class="donut-segment"
            cx="60"
            cy="60"
            :r="radius"
            :stroke="segment.color"
            :stroke-dasharray="segment.dasharray"
            :stroke-dashoffset="segment.dashoffset"
          />
        </svg>
        <div class="donut-total">
          <strong>{{ total }}</strong>
          <span>Findings</span>
        </div>
      </div>

      <ul class="distribution-list">
        <li v-for="segment in segments" :key="segment.label">
          <span class="color-dot" :style="{ backgroundColor: segment.color }"></span>
          <span class="item-label">{{ segment.label }}</span>
          <strong>{{ segment.value }}</strong>
          <span class="percentage">{{ segment.percentage }}%</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.distribution-card {
  min-width: 0;
  padding: 22px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
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
  letter-spacing: -.01em;
}

.description {
  margin: 6px 0 0;
  color: var(--muted-text);
  font-size: 11px;
}

.distribution-body {
  display: grid;
  grid-template-columns: 132px minmax(150px, 1fr);
  align-items: center;
  gap: 18px;
  margin-top: 20px;
}

.donut-wrap {
  position: relative;
  width: 132px;
  height: 132px;
}

.donut-wrap svg {
  width: 100%;
  transform: rotate(-90deg);
}

.donut-track,
.donut-segment {
  fill: none;
  stroke-width: 12;
}

.donut-track {
  stroke: #edf1f5;
}

.donut-segment {
  stroke-linecap: butt;
}

.donut-total {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
}

.donut-total strong {
  color: var(--heading-color);
  font-size: 23px;
  line-height: 1;
}

.donut-total span {
  margin-top: 5px;
  color: var(--muted-text);
  font-size: 9px;
  text-transform: uppercase;
}

.distribution-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.distribution-list li {
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr) auto 34px;
  align-items: center;
  gap: 8px;
  color: #55677b;
  font-size: 10px;
}

.color-dot {
  width: 7px;
  height: 7px;
  border-radius: 2px;
}

.item-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.distribution-list strong {
  color: #30445a;
  font-size: 11px;
}

.percentage {
  color: #8a99aa;
  text-align: right;
}

@media (max-width: 420px) {
  .distribution-body {
    grid-template-columns: 1fr;
  }

  .donut-wrap {
    margin: 0 auto;
  }
}
</style>

