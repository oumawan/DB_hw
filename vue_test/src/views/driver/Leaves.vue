<template>
  <div class="leaves-page">
    <h2>请假申请</h2>
    <div>
      <form @submit.prevent="submitLeave">
        <label>开始时间 <input type="datetime-local" v-model="tbegin" required /></label>
        <label>结束时间 <input type="datetime-local" v-model="tend" required /></label>
        <label>原因 <input v-model="reason" /></label>
        <div class="actions"><button type="submit">提交请假</button></div>
      </form>

      <h3 style="margin-top:16px">历史请假</h3>
      <div>未实现，先去数据库看</div>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'
import { apiService } from '@/api/api';
import { getUserFromLocal } from '@/plugins/storage';

export default {
  name: 'DriverLeaves',
  data() { return { tbegin: '', tend: '', reason: '', leaves: [] } },
  created() {
    try { const raw = localStorage.getItem('driverLeaves'); this.leaves = raw ? JSON.parse(raw) : [] } catch (e) { console.error('Failed to load driverLeaves from localStorage', e); this.leaves = [] }
  },
  methods: {
    async submitLeave() {
      const user = getUserFromLocal() || {}
      if (!user.uid) {
        service.show('无法识别用户身份，请重新登录', { type: 'error' })
        return
      }
      if (!this.tbegin || !this.tend || !this.reason) {
        service.show('请完整填写请假信息', { type: 'warning' })
        return
      }
      if (this.tbegin >= this.tend) {
        service.show('结束时间必须晚于开始时间', { type: 'warning' })
        return
      }
      const ok = await service.showConfirm('提交请假申请？', { type: 'warning', confirmText: '提交', cancelText: '取消' })
      if (!ok) return
      const rec = {uid:user.uid, tbegin: this.tbegin, tend: this.tend, reason: this.reason }
      try{
        const response = await apiService.addLeave(rec)
        if (!response || !response.success) {
          service.show(response && response.message ? response.message : '提交请假申请失败', { type: 'error' })
          return
        }
        service.show('请假申请已提交', { type: 'success' })
      }
      catch(err){
        service.show(err.response.data.message || '出现错误，联系网络或后端', { type: 'error' })
        return
      }
      finally {
        this.tbegin = this.tend = this.reason = ''
      }
    }
  }
}
</script>

<style scoped>
label { display: block; margin: 8px 0 }
input { padding: 6px; width: 300px }
.actions { margin-top: 8px }
</style>
