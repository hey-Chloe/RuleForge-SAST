<script setup lang="ts">
import type { ProjectSummary } from '../types/dashboard'

defineProps<{
  project: ProjectSummary
}>()
</script>

<template>
  <header class="app-header">
    <div class="project-context">
      <span class="eyebrow">当前项目</span>
      <div class="project-line">
        <strong>{{ project.name }}</strong>
        <span class="branch">{{ project.branch }}</span>
      </div>
    </div>

    <div class="header-actions">
      <div class="scan-state">
        <span class="state-dot" aria-hidden="true"></span>
        <div>
          <strong>{{ project.scanStatus }}</strong>
          <span>{{ project.scanTime }}</span>
        </div>
      </div>
      <button class="theme-placeholder" type="button" disabled title="深色模式将在后续版本开放" aria-label="深色模式将在后续版本开放">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20 15.2A8.5 8.5 0 0 1 8.8 4 8.5 8.5 0 1 0 20 15.2Z" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  min-height: 76px;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 14px clamp(20px, 3vw, 40px);
  background: rgba(255, 255, 255, .97);
  border-bottom: 1px solid var(--border-color);
}

.project-context,
.project-line,
.header-actions,
.scan-state {
  display: flex;
  align-items: center;
}

.project-context {
  align-items: flex-start;
  flex-direction: column;
  gap: 4px;
}

.eyebrow {
  color: var(--muted-text);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.project-line {
  gap: 9px;
}

.project-line strong {
  color: var(--heading-color);
  font-size: 16px;
}

.branch {
  padding: 3px 7px;
  color: #526982;
  font-family: var(--mono-font);
  font-size: 10px;
  background: #edf2f7;
  border: 1px solid #dce4ed;
  border-radius: 5px;
}

.header-actions {
  gap: 18px;
}

.scan-state {
  gap: 9px;
}

.scan-state > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.scan-state strong {
  color: #32475e;
  font-size: 12px;
  font-weight: 650;
}

.scan-state span:last-child {
  color: var(--muted-text);
  font-size: 10px;
}

.state-dot {
  width: 8px;
  height: 8px;
  background: #5d9a7f;
  border-radius: 50%;
}

.theme-placeholder {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  color: #7d8fa3;
  background: #f7f9fb;
  border: 1px solid var(--border-color);
  border-radius: 9px;
  cursor: default;
}

.theme-placeholder svg {
  width: 17px;
  fill: none;
  stroke: currentColor;
  stroke-linejoin: round;
  stroke-width: 1.7;
}

@media (max-width: 640px) {
  .app-header {
    position: relative;
    min-height: 68px;
    padding: 12px 16px;
  }

  .scan-state {
    display: none;
  }
}
</style>

