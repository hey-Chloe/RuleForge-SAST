<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import { projectSummary } from './data/dashboardMock'
import type { AppView } from './types/dashboard'
import DashboardView from './views/DashboardView.vue'
import ScansView from './views/ScansView.vue'
import VulnerabilitiesView from './views/VulnerabilitiesView.vue'

const activeView = ref<AppView>('dashboard')

function navigate(view: AppView): void {
  activeView.value = view
}
</script>

<template>
  <div class="app-shell">
    <AppSidebar :active-view="activeView" @navigate="navigate" />

    <div class="app-workspace">
      <AppHeader :project="projectSummary" />
      <main class="app-main">
        <DashboardView v-if="activeView === 'dashboard'" />
        <ScansView v-else-if="activeView === 'scans'" />
        <VulnerabilitiesView v-else />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-workspace {
  min-height: 100vh;
  margin-left: var(--sidebar-width);
}

.app-main {
  min-width: 0;
}

@media (max-width: 900px) {
  .app-workspace {
    margin-left: var(--sidebar-compact-width);
  }
}

@media (max-width: 640px) {
  .app-workspace {
    margin-left: 0;
  }
}
</style>
