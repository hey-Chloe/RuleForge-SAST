<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

interface LegacyFinding {
  rule: string
  file: string
  line: number
}

interface LegacyScanResult {
  vulnerabilities: LegacyFinding[]
}

const file = ref<File | null>(null)
const result = ref<LegacyScanResult | null>(null)
const loading = ref(false)

function chooseFile(event: Event): void {
  const input = event.target as HTMLInputElement
  file.value = input.files?.[0] ?? null
}

async function scan(): Promise<void> {
  if (!file.value) {
    window.alert('请选择文件')
    return
  }

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    loading.value = true
    const response = await axios.post<LegacyScanResult>(
      'http://127.0.0.1:8000/scan',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    result.value = response.data
  } catch (error: unknown) {
    console.error(error)
    window.alert('扫描失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="legacy-scan-panel">
    <h2>代码扫描</h2>
    <div class="upload">
      <input type="file" accept=".php" @change="chooseFile">
      <button type="button" @click="scan">{{ loading ? '扫描中...' : '开始扫描' }}</button>
    </div>

    <h3>扫描结果</h3>
    <div v-if="result">
      <article v-for="item in result.vulnerabilities" :key="`${item.file}-${item.line}`" class="vulnerability">
        <strong>{{ item.rule }}</strong>
        <span>{{ item.file }} · 第 {{ item.line }} 行</span>
      </article>
    </div>
    <p v-else>暂无扫描结果</p>
  </section>
</template>

<style scoped>
.legacy-scan-panel {
  padding: 24px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
}

.upload {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
}

button {
  padding: 9px 14px;
  color: #fff;
  background: var(--primary-color);
  border: 0;
  border-radius: 7px;
}

.vulnerability {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 10px;
  padding: 12px;
  background: #f7f9fb;
  border: 1px solid #e3e8ee;
  border-radius: 7px;
}
</style>
