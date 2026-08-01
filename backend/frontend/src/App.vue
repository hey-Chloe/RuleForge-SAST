<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import { projectSummary } from './data/dashboardMock'
import DashboardView from './views/DashboardView.vue'
</script>

<template>
  <div class="app-shell">
    <AppSidebar />

    <div class="app-workspace">
      <AppHeader :project="projectSummary" />
      <main class="app-main">
        <DashboardView />
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
