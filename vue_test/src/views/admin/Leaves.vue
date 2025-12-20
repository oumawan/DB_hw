<template>
  <div>
    <h2>请假管理</h2>
    <div style="margin-bottom:10px">
      <button @click="revokeExpired" style="background:#e74c3c;color:#fff;padding:6px 10px;border-radius:4px;border:none">删除过期请假</button>
    </div>
    <div>
      <table class="leaves-table">
        <thead>
          <tr>
            <th>请假人</th>
            <th>开始</th>
            <th>结束</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in leaves" :key="l.lid">
            <td>{{ l.name || l.uid }}</td>
            <td class="nowrap">{{ formatDate(l.tbegin) }}</td>
            <td class="nowrap">{{ formatDate(l.tend) }}</td>
            <td>{{ l.approved === 'Y' ? '已批准' : '未批准' }}</td>
            <td>
              <button @click="openReasonModal(l)">详细原因</button>
              <button @click="approve(l)" :disabled="l.approved === 'Y'">批准</button>
              <button @click="copyReason(l)">复制原因</button>
            </td>
          </tr>
          <tr v-if="leaves.length===0"><td colspan="5">暂无请假记录</td></tr>
        </tbody>
      </table>

      <!-- 顶层模态：只可通过 × 关闭（背景点击或 ESC 无效） -->
      <div v-if="reasonModal.visible" class="modal-overlay">
        <div class="modal-box" @click.stop>
          <button class="modal-close" @click="closeReasonModal">×</button>
          <h3>请假原因</h3>
          <div class="modal-body">{{ reasonModal.text || '-' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import service from '../../plugins/messageService'
import { apiService } from '@/api/api'
import { getUserFromLocal } from '@/plugins/storage'

export default {
  name: 'AdminLeaves',
  data() { return { leaves: [], reasonModal: { visible: false, text: '' } } },
  mounted() { this.load() },
  beforeUnmount() { if (this._blockEsc) window.removeEventListener('keydown', this._blockEsc) },
  methods: {
    shortReason(r) { if (!r) return '-'; return r.length>30? r.slice(0,30)+'...': r },
    formatDate(v){ if(!v) return '-'; try{ const d=new Date(v); if(isNaN(d.getTime())) return v; return d.toLocaleString() }catch(e){ return v } },
    async load(){
      const user = getUserFromLocal() || {}
      const depotID = user.depotID || null
      try{
        const resp = await apiService.fetchLeavesByDepot({ depotID })
        const data = resp && resp.data ? resp.data : resp
        if (!data || data.success === false) {
          service.show(data && data.message ? data.message : '加载请假记录失败', { type: 'error' })
          this.leaves = []
          return
        }
        // expect data.leaves
        this.leaves = (data.leaves || []).map(l => ({ ...l }))
      } catch (err) {
        console.error(err)
        service.show('加载请假记录失败', { type: 'error' })
        this.leaves = []
      }
    },
    showReason(l){ service.show(l.reason || '-', { type: 'info' }) },
    openReasonModal(l){ this.reasonModal.text = l.reason || '-'; this.reasonModal.visible = true; this._blockEsc = (e)=>{ if (e.key==='Escape'){ e.stopPropagation(); e.preventDefault(); } }; window.addEventListener('keydown', this._blockEsc) },
    closeReasonModal(){ this.reasonModal.visible = false; if (this._blockEsc) { window.removeEventListener('keydown', this._blockEsc); this._blockEsc = null } },
    copyReason(l){ try{ navigator.clipboard.writeText(l.reason||''); service.show('已复制原因', { type: 'success' }) }catch(e){ service.show('复制失败', { type: 'error' }) } },
    async approve(l){
      const ok = await service.showConfirm('确认批准该请假？', { type: 'warning', confirmText: '批准', cancelText: '取消' })
      if (!ok) return
      try{
        const resp = await apiService.approveLeave({ lid: l.lid })
        const data = resp && resp.data ? resp.data : resp
        if (data && data.success) {
          service.show('批准成功', { type: 'success' })
          this.load()
        } else {
          service.show(data && data.message ? data.message : '批准失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('批准失败', { type: 'error' })
      }
    }
    ,
    async revokeExpired(){
      const ok = await service.showConfirm('确认删除 7 天之前已结束的请假记录？该操作不可恢复', { type: 'warning', confirmText: '删除', cancelText: '取消' })
      if (!ok) return
      try{
        // 计算 7 天前的日期（格式 YYYY-MM-DD），并传给后端
        const d = new Date()
        d.setDate(d.getDate() - 6)
        const cutoff = d.toISOString().slice(0,10)
        const resp = await apiService.revokeExpiredLeaves({ date: cutoff })
        const data = resp && resp.data ? resp.data : resp
        if (data && data.success) {
          service.show(`已删除 ${data.deleted || 0} 条过期请假`, { type: 'success' })
          this.load()
        } else {
          service.show(data && data.message ? data.message : '删除失败', { type: 'error' })
        }
      }catch(err){
        console.error(err)
        service.show('删除失败', { type: 'error' })
      }
    }
  }
}
</script>

<style scoped>
.leaves-table { width:100%; border-collapse:collapse }
.leaves-table th, .leaves-table td { padding:8px; border:1px solid #eee; text-align:left }
.nowrap { white-space:nowrap }
button { margin-right:6px }

/* modal styles */
.modal-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.35); z-index:9999 }
.modal-box { background: #fff; padding:20px; border-radius:6px; width:80%; max-width:640px; box-shadow:0 8px 24px rgba(0,0,0,0.2); position:relative }
.modal-close { position:absolute; right:8px; top:6px; border:none; background:transparent; font-size:20px; cursor:pointer }
.modal-body { margin-top:12px; white-space:pre-wrap }
</style>
