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
      <div>
        <table class="leaves-table">
          <thead>
            <tr>
              <th>开始</th>
              <th>结束</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in leaves" :key="l.lid">
              <td class="nowrap">{{ formatDate(l.tbegin) }}</td>
              <td class="nowrap">{{ formatDate(l.tend) }}</td>
              <td>{{ l.approved === 'Y' ? '已批准' : '未批准' }}</td>
              <td>
                <button @click="openReasonModal(l)">详细原因</button>
                <button @click="copyReason(l)">复制原因</button>
              </td>
            </tr>
            <tr v-if="leaves.length===0"><td colspan="4">暂无请假记录</td></tr>
          </tbody>
        </table>

        <div v-if="reasonModal.visible" class="modal-overlay">
          <div class="modal-box" @click.stop>
            <button class="modal-close" @click="closeReasonModal">×</button>
            <h3>请假原因</h3>
            <div class="modal-body">{{ reasonModal.text || '-' }}</div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'
import api, { apiService } from '@/api/api';
import { getUserFromLocal } from '@/plugins/storage';

export default {
  name: 'DriverLeaves',
  data() { return { tbegin: '', tend: '', reason: '', leaves: [], reasonModal: { visible: false, text: '' } } },
  mounted() { this.load() },
  beforeUnmount() { if (this._blockEsc) window.removeEventListener('keydown', this._blockEsc) },
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
        // refresh list after submit
        this.load()
      }
      catch(err){
        service.show(err?.response?.data?.message || '出现错误，联系网络或后端', { type: 'error' })
        return
      }
      finally {
        this.tbegin = this.tend = this.reason = ''
      }
    },
    async load(){
      const user = getUserFromLocal() || {}
      if (!user.uid) { this.leaves = []; return }
      try{
        const resp = await api.post('api/admin/leave/fetchByDriver/', { uid: user.uid })
        const data = resp && resp.data ? resp.data : resp
        if (!data || data.success === false) {
          service.show(data && data.message ? data.message : '加载请假记录失败', { type: 'error' })
          this.leaves = []
          return
        }
        this.leaves = (data.leaves || [])
      } catch (err) {
        console.error(err)
        service.show('加载请假记录失败', { type: 'error' })
        this.leaves = []
      }
    },
    formatDate(v){ if(!v) return '-'; try{ const d=new Date(v); if(isNaN(d.getTime())) return v; return d.toLocaleString() }catch(e){ return v } },
    openReasonModal(l){ this.reasonModal.text = l.reason || '-'; this.reasonModal.visible = true; this._blockEsc = (e)=>{ if (e.key==='Escape'){ e.stopPropagation(); e.preventDefault(); } }; window.addEventListener('keydown', this._blockEsc) },
    closeReasonModal(){ this.reasonModal.visible = false; if (this._blockEsc) { window.removeEventListener('keydown', this._blockEsc); this._blockEsc = null } },
    copyReason(l){ try{ navigator.clipboard.writeText(l.reason||''); service.show('已复制原因', { type: 'success' }) }catch(e){ service.show('复制失败', { type: 'error' }) } }
  }
}
</script>

<style scoped>
label { display: block; margin: 8px 0 }
input { padding: 6px; width: 300px }
.actions { margin-top: 8px }
/* reuse modal/table styles */
.leaves-table { width:100%; border-collapse:collapse; margin-top:12px }
.leaves-table th, .leaves-table td { padding:8px; border:1px solid #eee; text-align:left }
.nowrap { white-space:nowrap }
button { margin-right:6px }
.modal-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.35); z-index:9999 }
.modal-box { background: #fff; padding:20px; border-radius:6px; width:80%; max-width:640px; box-shadow:0 8px 24px rgba(0,0,0,0.2); position:relative }
.modal-close { position:absolute; right:8px; top:6px; border:none; background:transparent; font-size:20px; cursor:pointer }
.modal-body { margin-top:12px; white-space:pre-wrap }
</style>
