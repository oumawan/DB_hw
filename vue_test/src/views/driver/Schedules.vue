<template>
  <div class="schedules-page">
    <h2>我的班次</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <div v-if="schedules.length === 0">暂无班次</div>
      <ul>
        <li v-for="s in schedules" :key="s.sid" class="sched-item">
          <div>
            <strong>{{ s.sid }}</strong> — {{ s.lineNo }} · {{ new Date(s.dtime).toLocaleString() }}
            <div>车辆: {{ s.vid }} · 出发: {{ s.dloc }}</div>
          </div>
          <div>
            <span v-if="s.completed" class="done">已完成</span>
            <button v-else @click="confirmComplete(s)">确认完成</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'

export default {
  name: 'DriverSchedules',
  data() { return { loading: true, schedules: [] } },
  created() {
    try {
      const raw = localStorage.getItem('driverSchedules')
      if (raw) this.schedules = JSON.parse(raw)
      else this.schedules = []
    } catch (e) { console.error('Failed to load driverSchedules', e); this.schedules = [] }
    this.loading = false
  },
  methods: {
    async confirmComplete(s) {
      const ok = await service.showConfirm(`确认已完成班次 ${s.sid} 吗？`, { type: 'success', confirmText: '已完成', cancelText: '取消' })
      if (!ok) return
      const idx = this.schedules.findIndex(x => x.sid === s.sid)
      if (idx !== -1) {
        this.schedules[idx].completed = true
        this.schedules[idx].completedAt = new Date().toISOString()
        try { localStorage.setItem('driverSchedules', JSON.stringify(this.schedules)) } catch (e) { console.error('Failed to save driverSchedules', e) }
        service.show(`班次 ${s.sid} 已确认完成`, { type: 'success' })
      }
    }
  }
}
</script>

<style scoped>
.sched-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee }
.sched-item .done { color: #6b7280 }
.sched-item button { background: #10b981; color: #fff; border: none; padding: 6px 10px; border-radius: 6px }
</style>
