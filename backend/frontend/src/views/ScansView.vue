<script setup lang="ts">
import LegacyScanPanel from '../components/LegacyScanPanel.vue'
</script>

<template>
  <section class="scans-view" aria-labelledby="scans-title">
    <header class="view-intro">
      <div>
        <span class="view-eyebrow">Semgrep scan</span>
        <h1 id="scans-title">代码扫描</h1>
        <p>上传 PHP 源码，并从本地真实规则库选择一条规则执行扫描。</p>
      </div>
      <div class="service-state">
        <span class="service-dot" aria-hidden="true"></span>
        <div>
          <span>扫描服务</span>
          <strong>Local FastAPI</strong>
        </div>
      </div>
    </header>

    <aside class="scope-notice" aria-label="当前扫描支持范围">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 10v6m0-9h.01" />
      </svg>
      <div>
        <strong>当前版本支持上传单个 PHP 文件，并选择一条真实 PHP 规则。</strong>
        <p>规则来自 GET /rules；每次扫描只执行一条规则，不支持多文件或批量规则。</p>
      </div>
    </aside>

    <LegacyScanPanel />
  </section>
</template>

<style scoped>
.scans-view {
  width: min(100%, 1320px);
  margin: 0 auto;
  padding: clamp(24px, 3vw, 40px);
}

.view-intro {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.view-eyebrow {
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

.service-state {
  display: flex;
  align-items: center;
  gap: 10px;
}

.service-dot {
  width: 9px;
  height: 9px;
  background: #6c849d;
  border-radius: 50%;
}

.service-state div {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}

.service-state span {
  color: var(--muted-text);
  font-size: 10px;
}

.service-state strong {
  color: #40566d;
  font-family: var(--mono-font);
  font-size: 11px;
}

.scope-notice {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  margin-bottom: 18px;
  padding: 16px 18px;
  background: #edf3f7;
  border: 1px solid #d8e3eb;
  border-radius: 10px;
}

.scope-notice svg {
  width: 19px;
  flex: 0 0 19px;
  fill: none;
  stroke: #5f7b97;
  stroke-linecap: round;
  stroke-width: 1.6;
}

.scope-notice strong {
  color: #395169;
  font-size: 12px;
}

.scope-notice p {
  margin: 5px 0 0;
  color: #6f7f91;
  font-size: 11px;
}

@media (max-width: 640px) {
  .scans-view {
    padding: 20px 16px 28px;
  }

  .view-intro {
    align-items: flex-start;
    flex-direction: column;
  }

  .service-state div {
    align-items: flex-start;
  }
}
</style>
