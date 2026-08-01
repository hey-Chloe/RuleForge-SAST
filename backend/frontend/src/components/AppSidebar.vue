<script setup lang="ts">
import type { AppView } from '../types/dashboard'

interface NavigationItem {
  label: string
  icon: 'dashboard' | 'scan' | 'shield' | 'rules' | 'report'
  page: AppView | null
}

const props = defineProps<{
  activeView: AppView
}>()

const emit = defineEmits<{
  navigate: [view: AppView]
}>()

const navigation: NavigationItem[] = [
  { label: 'Dashboard', icon: 'dashboard', page: 'dashboard' },
  { label: 'Scans', icon: 'scan', page: 'scans' },
  { label: 'Vulnerabilities', icon: 'shield', page: 'vulnerabilities' },
  { label: 'Rules', icon: 'rules', page: 'rules' },
  { label: 'Reports', icon: 'report', page: 'reports' },
]

function navigate(item: NavigationItem): void {
  if (item.page && item.page !== props.activeView) {
    emit('navigate', item.page)
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">RF</div>
      <div class="brand-copy">
        <strong>RuleForge</strong>
        <span>SAST Platform</span>
      </div>
    </div>

    <p class="nav-label">Workspace</p>
    <nav class="navigation" aria-label="主导航">
      <button
        v-for="item in navigation"
        :key="item.label"
        class="nav-item"
        :class="{ active: item.page === activeView }"
        :disabled="item.page === null"
        :aria-current="item.page === activeView ? 'page' : undefined"
        :title="item.page ? item.label : `${item.label} 将在后续阶段开放`"
        type="button"
        @click="navigate(item)"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path v-if="item.icon === 'dashboard'" d="M4 4h6v6H4V4Zm10 0h6v10h-6V4ZM4 14h6v6H4v-6Zm10 4h6v2h-6v-2Z" />
          <path v-else-if="item.icon === 'scan'" d="M5 3h11l3 3v15H5V3Zm10 2v3h3M8 12h8M8 16h6" />
          <path v-else-if="item.icon === 'shield'" d="M12 3 5 6v5c0 4.6 2.8 8.1 7 10 4.2-1.9 7-5.4 7-10V6l-7-3Zm0 5v5m0 3h.01" />
          <path v-else-if="item.icon === 'rules'" d="M7 4h13M7 10h13M7 16h13M4 4h.01M4 10h.01M4 16h.01" />
          <path v-else d="M6 3h9l3 3v15H6V3Zm8 1v4h4M9 12h6M9 16h6" />
        </svg>
        <span>{{ item.label }}</span>
        <span v-if="item.page === null" class="soon">Soon</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <span class="status-dot" aria-hidden="true"></span>
      <div class="footer-copy">
        <strong>Local workspace</strong>
        <span>Semgrep rule engine</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 20;
  display: flex;
  width: var(--sidebar-width);
  flex-direction: column;
  padding: 24px 18px;
  color: #dce6f2;
  background: #142235;
  border-right: 1px solid #22354c;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px 26px;
}

.brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  place-items: center;
  color: #eff6ff;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  background: #4f6f96;
  border: 1px solid #6f89a8;
  border-radius: 10px;
}

.brand-copy,
.footer-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.brand-copy strong {
  color: #fff;
  font-size: 16px;
  letter-spacing: -.01em;
}

.brand-copy span,
.footer-copy span {
  margin-top: 2px;
  color: #8fa2b9;
  font-size: 11px;
}

.nav-label {
  margin: 8px 10px 10px;
  color: #72879f;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .13em;
  text-transform: uppercase;
}

.navigation {
  display: grid;
  gap: 6px;
}

.nav-item {
  display: flex;
  width: 100%;
  min-height: 44px;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  color: #aebdd0;
  text-align: left;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 9px;
}

.nav-item svg {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.7;
}

.nav-item svg path:first-child {
  fill: none;
}

.nav-item.active {
  color: #f5f8fc;
  background: #243a53;
  border-color: #304b68;
  box-shadow: inset 3px 0 0 #7f9dbe;
}

.nav-item:disabled {
  cursor: default;
  opacity: .62;
}

.soon {
  margin-left: auto;
  color: #72879f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  padding: 15px 12px 2px;
  border-top: 1px solid #293a50;
}

.status-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  background: #69a68c;
  border-radius: 50%;
}

.footer-copy strong {
  color: #dce6f2;
  font-size: 11px;
}

@media (max-width: 900px) {
  .sidebar {
    align-items: center;
    padding-inline: 12px;
  }

  .brand {
    padding-inline: 0;
  }

  .brand-copy,
  .nav-label,
  .nav-item > span,
  .footer-copy {
    display: none;
  }

  .nav-item {
    width: 48px;
    justify-content: center;
    padding: 0;
  }

  .sidebar-footer {
    padding-inline: 0;
  }
}

@media (max-width: 640px) {
  .sidebar {
    position: relative;
    inset: auto;
    width: 100%;
    height: 66px;
    flex-direction: row;
    padding: 10px 14px;
  }

  .brand {
    padding: 0;
  }

  .brand-mark {
    width: 36px;
    height: 36px;
    flex-basis: 36px;
  }

  .navigation {
    display: flex;
    gap: 2px;
    margin-left: auto;
  }

  .nav-item {
    width: 40px;
    min-height: 40px;
  }

  .sidebar-footer {
    display: none;
  }
}
</style>
