<script setup lang="ts">
import DistributionChart from '../components/DistributionChart.vue'
import RecentFindingsTable from '../components/RecentFindingsTable.vue'
import StatCard from '../components/StatCard.vue'
import TrendChart from '../components/TrendChart.vue'
import {
  dashboardMetrics,
  recentFindings,
  trendPoints,
  vulnerabilityDistribution,
} from '../data/dashboardMock'
</script>

<template>
  <section class="dashboard-view" aria-labelledby="dashboard-title">
    <header class="dashboard-intro">
      <div>
        <span class="dashboard-intro__eyebrow">Security overview</span>
        <h1 id="dashboard-title">代码安全概览</h1>
        <p>集中查看静态代码扫描风险、漏洞分布和最近发现。</p>
      </div>

      <div class="dashboard-intro__scope" aria-label="当前扫描范围">
        <span>当前扫描范围</span>
        <strong>3 种语言 · 18 条规则</strong>
      </div>
    </header>

    <div class="dashboard-stats" aria-label="漏洞统计">
      <StatCard
        v-for="metric in dashboardMetrics"
        :key="metric.label"
        :metric="metric"
      />
    </div>

    <div class="dashboard-analytics">
      <TrendChart :points="trendPoints" />
      <DistributionChart :items="vulnerabilityDistribution" />
    </div>

    <RecentFindingsTable :findings="recentFindings" />
  </section>
</template>

<style scoped>
.dashboard-view {
  width: min(100%, 1520px);
  margin: 0 auto;
  padding: clamp(24px, 3vw, 40px);
}

.dashboard-intro {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
}

.dashboard-intro__eyebrow {
  display: block;
  margin-bottom: 8px;
  color: var(--primary);
  font-size: 0.72rem;
  font-weight: 750;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.dashboard-intro h1 {
  margin: 0;
  color: var(--heading);
  font-size: clamp(1.65rem, 2.1vw, 2.15rem);
  line-height: 1.2;
  letter-spacing: -0.035em;
}

.dashboard-intro p {
  margin: 9px 0 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.dashboard-intro__scope {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 190px;
}

.dashboard-intro__scope span {
  color: var(--muted);
  font-size: 0.75rem;
}

.dashboard-intro__scope strong {
  color: var(--text);
  font-size: 0.88rem;
  font-weight: 650;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.dashboard-analytics {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(320px, 0.9fr);
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 1180px) {
  .dashboard-analytics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1080px) {
  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .dashboard-view {
    padding: 20px 16px 28px;
  }

  .dashboard-intro {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 22px;
  }

  .dashboard-intro__scope {
    align-items: flex-start;
  }

  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}
</style>
