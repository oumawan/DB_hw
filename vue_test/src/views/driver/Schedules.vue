<template>
  <div class="schedules-page">
    <h2>我的班次</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <div v-if="schedules.length === 0">暂无班次</div>
      <table class="schedules-table" v-else>
        <thead>
          <tr>
            <th>SID</th>
            <th>出发时间</th>
            <th>预计到达时间</th>
            <th>起点 → 终点</th>
            <th>驾驶车辆</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in schedules" :key="s.sid">
            <td>{{ s.sid }}</td>
            <td class="nowrap">{{ formatDate(s.dtime) }}</td>
            <td class="nowrap">{{ formatDate(s.atime) }}</td>
            <td>{{ s.lineFrom }} → {{ s.lineTo }}</td>
            <td>{{ s.lp || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'
import { apiService } from '@/api/api'
import { getUserFromLocal } from '@/plugins/storage'

export default {
  name: 'DriverSchedules',
  data() { return { loading: true, schedules: [] } },
  mounted() { this.load() },
  methods: {
    normalizeServerTime(v) {
      if (!v) return v
      if (typeof v !== 'string') return v
      if (v.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(v)) return v
      return v.replace(' ', 'T') + 'Z'
    },
    formatDate(v) { if (!v) return '-'; try { const d = new Date(v); if (isNaN(d.getTime())) return v; return d.toLocaleString() } catch(e) { return v } },
    async load() {
      this.loading = true
      this.schedules = []
      try {
        const user = getUserFromLocal() || {}
        const uid = user.uid || null
        if (!uid) {
          service.show('未检测到司机身份，请重新登录', { type: 'error' })
          this.loading = false
          return
        }
        const res = await apiService.fetchSchedulesForDriver({ uid })
        if (res && res.success) {
          this.schedules = (res.schedules || []).map(s => ({
            sid: s.sid,
            dtime: this.normalizeServerTime(s.dtime),
            atime: this.normalizeServerTime(s.atime),
            lineFrom: s.lineFrom,
            lineTo: s.lineTo,
            lp: s.lp
          }))
        } else {
          service.show(res && res.message ? res.message : '加载班次失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('加载班次失败', { type: 'error' })
      } finally {
        this.loading = false
      }
    },
    
  }
}
</script>

<style scoped>
.sched-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee }
.sched-item .done { color: #6b7280 }
.schedules-table { width:100%; border-collapse:collapse; margin-top:12px }
.schedules-table th, .schedules-table td { padding:8px; border:1px solid #eee; text-align:left }
.schedules-table th { background:#f3f4f6 }
.nowrap { white-space:nowrap }
</style>
