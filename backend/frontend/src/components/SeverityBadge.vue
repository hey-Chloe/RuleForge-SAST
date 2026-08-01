<script setup lang="ts">
import { computed } from 'vue'
import type { Severity } from '../types/dashboard'

const props = defineProps<{
  severity: Severity
}>()

const severityClass = computed(() => `severity-${props.severity.toLowerCase()}`)
</script>

<template>
  <span class="severity-badge" :class="severityClass">{{ severity }}</span>
</template>

<style scoped>
.severity-badge {
  display: inline-flex;
  min-width: 66px;
  justify-content: center;
  padding: 5px 9px;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: .04em;
  border: 1px solid transparent;
  border-radius: 999px;
}

.severity-critical {
  color: #9f303b;
  background: #fbebed;
  border-color: #f3cdd2;
}

.severity-high {
  color: #9f5629;
  background: #fff0e5;
  border-color: #f3d5be;
}

.severity-medium {
  color: #846b20;
  background: #fbf4d8;
  border-color: #ebdfa8;
}

.severity-low {
  color: #4c697f;
  background: #edf3f7;
  border-color: #d5e0e8;
}

.severity-unknown {
  color: #667384;
  background: #f0f2f5;
  border-color: #dde2e7;
}
</style>
