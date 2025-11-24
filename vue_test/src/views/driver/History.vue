<template>
  <div class="history-page">
    <h2>历史班次</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <div v-if="history.length === 0">暂无历史记录</div>
      <ul>
        <li v-for="s in history" :key="s.sid">
          <strong>{{ s.sid }}</strong> — {{ s.lineNo }} · 完成于 {{ new Date(s.completedAt).toLocaleString() }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriverHistory',
  data() { return { loading: true, history: [] } },
  created() {
    try {
      const raw = localStorage.getItem('driverSchedules')
      const arr = raw ? JSON.parse(raw) : []
      this.history = arr.filter(s => s.completed)
    } catch (e) { this.history = [] }
    this.loading = false
  }
}
</script>

<style scoped>
li { margin: 8px 0 }
</style>
