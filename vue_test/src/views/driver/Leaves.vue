<template>
  <div class="leaves-page">
    <h2>请假申请</h2>
    <div>
      <form @submit.prevent="submitLeave">
        <label>开始时间 <input type="datetime-local" v-model="tbegin" required /></label>
        <label>结束时间 <input type="datetime-local" v-model="tend" required /></label>
        <label>备注 <input v-model="note" /></label>
        <div class="actions"><button type="submit">提交请假</button></div>
      </form>

      <h3 style="margin-top:16px">历史请假</h3>
      <div v-if="leaves.length === 0">暂无历史请假</div>
      <ul>
        <li v-for="l in leaves" :key="l.tbegin">{{ new Date(l.tbegin).toLocaleString() }} → {{ new Date(l.tend).toLocaleString() }} — {{ l.note }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'

export default {
  name: 'DriverLeaves',
  data() { return { tbegin: '', tend: '', note: '', leaves: [] } },
  created() {
    try { const raw = localStorage.getItem('driverLeaves'); this.leaves = raw ? JSON.parse(raw) : [] } catch (e) { console.error('Failed to load driverLeaves from localStorage', e); this.leaves = [] }
  },
  methods: {
    async submitLeave() {
      const ok = await service.showConfirm('提交请假申请？', { type: 'warning', confirmText: '提交', cancelText: '取消' })
      if (!ok) return
      const rec = { tbegin: this.tbegin, tend: this.tend, note: this.note }
      this.leaves.unshift(rec)
      try { localStorage.setItem('driverLeaves', JSON.stringify(this.leaves)) } catch (e) { console.error('Failed to save driverLeaves to localStorage', e) }
      service.show('请假申请已提交（模拟）', { type: 'success' })
      this.tbegin = this.tend = this.note = ''
    }
  }
}
</script>

<style scoped>
label { display: block; margin: 8px 0 }
input { padding: 6px; width: 300px }
.actions { margin-top: 8px }
</style>
