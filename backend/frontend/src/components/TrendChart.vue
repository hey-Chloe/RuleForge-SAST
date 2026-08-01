<script setup lang="ts">
import { computed } from 'vue'
import type { TrendPoint } from '../types/dashboard'

const props = defineProps<{
  points: TrendPoint[]
}>()

const chartWidth = 720
const chartHeight = 244
const padding = { top: 18, right: 18, bottom: 38, left: 44 }
const plotWidth = chartWidth - padding.left - padding.right
const plotHeight = chartHeight - padding.top - padding.bottom

const maxValue = computed(() => {
  const highest = Math.max(1, ...props.points.map((point) => point.value))
  return Math.ceil(highest / 10) * 10
})

const xPosition = (index: number): number => {
  if (props.points.length <= 1) return padding.left
  return padding.left + (index / (props.points.length - 1)) * plotWidth
}

const yPosition = (value: number): number => (
  padding.top + plotHeight - (value / maxValue.value) * plotHeight
)

const polylinePoints = computed(() => (
  props.points
    .map((point, index) => `${xPosition(index)},${yPosition(point.value)}`)
    .join(' ')
))

const gridLines = computed(() => [0, .25, .5, .75, 1].map((ratio) => ({
  y: padding.top + plotHeight - ratio * plotHeight,
  value: Math.round(maxValue.value * ratio),
})))
</script>

<template>
  <section class="chart-card">
    <div class="card-heading">
      <div>
        <span class="section-kicker">趋势</span>
        <h2>Vulnerability Trend</h2>
        <p>近七次扫描的漏洞数量变化</p>
      </div>
      <div class="legend"><span></span> Findings</div>
    </div>

    <div class="chart-wrap" role="img" aria-label="近七次扫描漏洞趋势折线图">
      <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" preserveAspectRatio="xMidYMid meet">
        <g class="grid">
          <g v-for="line in gridLines" :key="line.y">
            <line :x1="padding.left" :x2="chartWidth - padding.right" :y1="line.y" :y2="line.y" />
            <text :x="padding.left - 10" :y="line.y + 4" text-anchor="end">{{ line.value }}</text>
          </g>
        </g>

        <polyline class="trend-line" :points="polylinePoints" />

        <g v-for="(point, index) in points" :key="point.label" class="data-point">
          <circle :cx="xPosition(index)" :cy="yPosition(point.value)" r="4" />
          <text :x="xPosition(index)" :y="chartHeight - 12" text-anchor="middle">{{ point.label }}</text>
        </g>
      </svg>
    </div>
  </section>
</template>

<style scoped>
.chart-card {
  min-width: 0;
  padding: 22px 22px 16px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

.card-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
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

p {
  margin: 6px 0 0;
  color: var(--muted-text);
  font-size: 11px;
}

.legend {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #66778a;
  font-size: 10px;
}

.legend span {
  width: 16px;
  height: 2px;
  background: var(--primary-color);
}

.chart-wrap {
  width: 100%;
  margin-top: 18px;
  overflow: hidden;
}

svg {
  display: block;
  width: 100%;
  min-width: 560px;
}

.grid line {
  stroke: #e7ecf2;
  stroke-dasharray: 3 4;
}

.grid text,
.data-point text {
  fill: #8b99aa;
  font-size: 10px;
}

.trend-line {
  fill: none;
  stroke: var(--primary-color);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.5;
}

.data-point circle {
  fill: #fff;
  stroke: var(--primary-color);
  stroke-width: 2.5;
}

@media (max-width: 640px) {
  .chart-card {
    padding-inline: 16px;
  }

  .chart-wrap {
    overflow-x: auto;
  }
}
</style>

