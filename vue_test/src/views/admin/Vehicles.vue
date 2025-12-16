<template>
  <div class="admin-vehicles">
    <header class="toolbar">
      <h2>车辆管理</h2>
      <div class="controls">
        <button @click="openAdd">添加车辆</button>
      </div>
      <!-- 删除确认将使用 messageService.showConfirm() 显示，不再使用模板内 HTML 模态 -->
      <!-- Transfer Modal -->
      <div v-if="showTransfer" class="modal-backdrop">
        <div class="modal">
          <h3>调拨车辆</h3>
          <label>当前车场 <div class="readonly-field">{{ transferTarget.fromDepot || '未知' }}</div></label>
          <label>目标车场 <input v-model="transferForm.toDepot" placeholder="填写目标车场 ID" /></label>
          <label>备注 <input v-model="transferForm.note" placeholder="备注（可选）" /></label>
          <div class="modal-actions">
            <button @click="confirmTransfer" :disabled="transferring">{{ transferring ? '调拨中...' : '确认调拨' }}</button>
            <button @click="cancelTransfer" :disabled="transferring">取消</button>
          </div>
        </div>
      </div>
        <!-- History Modal -->
        <div v-if="showHistory" class="modal-backdrop">
          <div class="modal history-modal" style="width:800px; max-height:70vh; overflow:auto">
            <h3>车辆调动历史 - 车辆编号: {{ historyTarget.vid }}</h3>
            <div v-if="historyLoading">加载中…</div>
            <div v-else>
              <table class="history-table">
                <thead>
                  <tr>
                    <th>来源车场</th>
                    <th>目标车场</th>
                    <th>日期</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(t, idx) in historyList" :key="idx">
                    <td>{{ t.fromDepot }}</td>
                    <td>{{ t.toDepot }}</td>
                    <td class="date-cell">{{ formatDate(t.date) }}</td>
                    <td class="note-cell">{{ t.note }}</td>
                  </tr>
                  <tr v-if="historyList.length===0"><td colspan="4">暂无调动记录</td></tr>
                </tbody>
              </table>
            </div>
            <div class="modal-actions">
              <button @click="closeHistory">关闭</button>
            </div>
          </div>
        </div>
    </header>

    <section class="filters">
      <label>车牌号 <input v-model="lpFilter" placeholder="按车牌号搜索" /></label>
      <label>车辆类型
        <select v-model="vtypeFilter">
          <option value="">全部</option>
          <option>大型客车</option>
          <option>重型牵引挂车</option>
          <option>城市公交车</option>
          <option>中型客车</option>
          <option>大型货车</option>
          <option>小型汽车</option>
          <option>小型自动挡汽车</option>
        </select>
      </label>
      
      <div class="filter-actions">
        <button @click="applyFilters">应用筛选</button>
        <button @click="clearFilters">清除筛选</button>
      </div>
    </section>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <!-- Add Vehicle Modal -->
      <div v-if="showAdd" class="modal-backdrop">
        <div class="modal">
          <h3>添加车辆</h3>
          <label>车牌号 <input v-model="newVehicle.lp" /></label>
          <label>类型
            <select v-model="newVehicle.vtype">
              <option value="">请选择类型</option>
              <option>大型客车</option>
              <option>重型牵引挂车</option>
              <option>城市公交车</option>
              <option>中型客车</option>
              <option>大型货车</option>
              <option>小型汽车</option>
              <option>小型自动挡汽车</option>
            </select>
          </label>
          
          <label>车场 <div class="readonly-field">{{ newVehicle.depotID || '未指定' }}</div></label>
          <div class="modal-actions">
            <button @click="createVehicle" :disabled="adding">{{ adding ? '添加中...' : '保存' }}</button>
            <button @click="closeAdd" :disabled="adding">取消</button>
          </div>
        </div>
      </div>
      <table class="vehicles-table">
        <thead>
          <tr>
            <th>车辆编号</th>
            <th>车牌号</th>
            <th>类型</th>
            <th>车场</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in paged" :key="v.vid">
            <td>{{ v.vid }}</td>
            <td>{{ v.lp }}</td>
            <td>{{ v.vtype }}</td>
            <td>{{ v.depotID }}</td>
            <td>
                <button @click="openHistory(v)">历史</button>
                <button @click="transferTo(v)">调拨</button>
                <button @click="removeVehicle(v)" class="danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page<=1 || loading" @click="loadPage(1)">« 首页</button>
        <button :disabled="page<=1 || loading" @click="loadPage(page-1)">‹ 上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
        <button :disabled="page>=totalPages || loading" @click="loadPage(page+1)">下一页 ›</button>
        <button :disabled="page>=totalPages || loading" @click="loadPage(totalPages)">末页 »</button>
        <select v-model.number="pageSize" @change="onPageSizeChange">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { apiService } from '@/api/api'
import service from '../../plugins/messageService'
import { getUserFromLocal } from '../../plugins/storage'

export default {
  name: 'AdminVehicles',
  setup() {
    const vehicles = ref([])
    const loading = ref(false)
    const error = ref(null)
    const page = ref(1)
    const pageSize = ref(10)
    const total = ref(0)

    const lpFilter = ref('')
    const vtypeFilter = ref('')

    const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

    // paged is computed directly from vehicles.value which will already be filtered
    const paged = computed(() => {
      const p = Math.max(1, Number(page.value) || 1)
      const ps = Math.max(1, Number(pageSize.value) || 10)
      const start = (p - 1) * ps
      return vehicles.value.slice(start, start + ps)
    })

    async function loadPage(p = 1) {
      loading.value = true
      error.value = null
      try {
        const user = getUserFromLocal()
        const adminDepot = (user && user.depotID) ? user.depotID : ''
        const data = await apiService.fetchAllVehicles({ depotID: adminDepot })
        if (data && data.success === false) {
          service.show('加载车辆列表失败: ' + (data.message || '未知错误'), { type: 'error' })
          loading.value = false
          return
        }
        const list = (data && data.vehicles) ? data.vehicles : []
        // client-side filter happens here (only when loadPage is called)
        let filteredList = list.slice()
        if (lpFilter.value && String(lpFilter.value).trim()) {
          const q = String(lpFilter.value).toLowerCase()
          filteredList = filteredList.filter(v => v.lp && v.lp.toLowerCase().includes(q))
        }
        if (vtypeFilter.value && String(vtypeFilter.value).trim()) {
          const q = String(vtypeFilter.value)
          filteredList = filteredList.filter(v => v.vtype && v.vtype === q)
        }
        // ensure depotID present and set vehicles to filtered results
        vehicles.value = filteredList.map(v => ({ depotID: v.depotID || adminDepot, ...v }))
        total.value = vehicles.value.length
        page.value = p
      } catch (err) {
        error.value = err
        service.show('加载车辆列表失败', { type: 'error' })
      } finally {
        loading.value = false
      }
    }

    const showAdd = ref(false)
    const adding = ref(false)
    const newVehicle = ref({ lp: '', vtype: '', depotID: '' })

    // delete state (confirmation handled by messageService)
    const deleting = ref(false)

    function openAdd() {
      const user = getUserFromLocal()
      const adminDepot = (user && user.depotID) ? user.depotID : ''
      newVehicle.value = { lp: '', vtype: '', depotID: adminDepot }
      showAdd.value = true
    }

    function closeAdd() {
      showAdd.value = false
    }

    async function createVehicle() {
      if (!newVehicle.value.lp || !String(newVehicle.value.lp).trim()) {
        service.show('请填写车牌号', { type: 'error' })
        return
      }
      // ensure depot present
      if (!newVehicle.value.depotID) {
        const user2 = getUserFromLocal()
        if (user2 && user2.depotID) {
          newVehicle.value.depotID = user2.depotID
        } else {
          service.show('车场信息缺失，无法添加', { type: 'error' })
          return
        }
      }
      adding.value = true
      try {
        const resp = await apiService.addVehicle(Object.assign({}, newVehicle.value))
        if (resp && resp.success) {
          service.show('添加车辆成功', { type: 'success' })
          showAdd.value = false
          await loadPage(1)
        } else {
          service.show(resp && resp.message ? resp.message : '添加失败', { type: 'error' })
        }
      } catch (err) {
        console.error('createVehicle error', err)
        const msg = err?.response?.data?.message || err.message || '添加失败'
        service.show(msg, { type: 'error' })
      } finally {
        adding.value = false
      }
    }

    function applyFilters() {
      // reload from API when user applies filters
      page.value = 1
      loadPage(1)
    }

    function clearFilters() {
      lpFilter.value = ''
      vtypeFilter.value = ''
      page.value = 1
      loadPage(1)
    }

    function onPageSizeChange() {
      page.value = 1
    }

    // history modal state
    const showHistory = ref(false)
    const historyLoading = ref(false)
    const historyList = ref([])
    const historyTarget = ref({ vid: '' })

    async function openHistory(v) {
      historyTarget.value = { vid: v.vid }
      showHistory.value = true
      historyLoading.value = true
      historyList.value = []
      try {
        const resp = await apiService.fetchAllTransferHistory({ vid: v.vid })
        if (resp && resp.success) {
          historyList.value = resp.transfers || []
        } else {
          service.show(resp && resp.message ? resp.message : '获取历史失败', { type: 'error' })
        }
      } catch (err) {
        console.error('openHistory error', err)
        const msg = err?.response?.data?.message || err.message || '获取历史失败'
        service.show(msg, { type: 'error' })
      } finally {
        historyLoading.value = false
      }
    }

    function closeHistory() {
      showHistory.value = false
      historyList.value = []
      historyTarget.value = { vid: '' }
    }

    function pad(n) { return (n < 10 ? '0' : '') + n }
    function formatDate(d) {
      if (!d) return ''
      try {
        const date = new Date(d)
        if (isNaN(date.getTime())) return ''
        return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
      } catch (e) { return '' }
    }

    // transfer modal state and actions
    const showTransfer = ref(false)
    const transferring = ref(false)
    const transferTarget = ref({ vid: '', fromDepot: '' })
    const transferForm = ref({ toDepot: '', note: '' })

    function transferTo(v) {
      // open transfer modal with fromDepot defaulted
      const user = getUserFromLocal()
      const adminDepot = (v.depotID) ? v.depotID : (user && user.depotID ? user.depotID : '')
      transferTarget.value = { vid: v.vid, fromDepot: adminDepot }
      transferForm.value = { toDepot: '', note: '' }
      showTransfer.value = true
    }

    function cancelTransfer() {
      showTransfer.value = false
      transferTarget.value = { vid: '', fromDepot: '' }
      transferForm.value = { toDepot: '', note: '' }
    }

    async function confirmTransfer() {
      if (!transferTarget.value || !transferTarget.value.vid) {
        service.show('缺少车辆信息，无法调拨', { type: 'error' })
        return
      }
      if (!transferForm.value.toDepot || String(transferForm.value.toDepot).trim() === '') {
        service.show('请填写目标车场', { type: 'error' })
        return
      }
      transferring.value = true
      try {
        const payload = {
          vid: transferTarget.value.vid,
          fromDepot: transferTarget.value.fromDepot,
          toDepot: transferForm.value.toDepot,
          date: new Date().toISOString(),
          note: transferForm.value.note || ''
        }
        const resp = await apiService.transferVehicle(payload)
        if (resp && resp.success) {
          service.show('调拨成功', { type: 'success' })
          showTransfer.value = false
          await loadPage(page.value || 1)
        } else {
          service.show(resp && resp.message ? resp.message : '调拨失败', { type: 'error' })
        }
      } catch (err) {
        console.error('confirmTransfer error', err)
        const msg = err?.response?.data?.message || err.message || '调拨失败'
        service.show(msg, { type: 'error' })
      } finally {
        transferring.value = false
      }
    }

    async function removeVehicle(v) {
      // use messageService modal confirmation instead of inline HTML modal
      const ok = await service.showConfirm(`确定删除车辆 ${v.lp || ''} (VID: ${v.vid}) 吗？此操作不可撤销。`, { type: 'warning', confirmText: '确认删除', cancelText: '取消' })
      if (!ok) return
      deleting.value = true
      try {
        const resp = await apiService.removeVehicle({ vid: v.vid })
        if (resp && resp.success) {
          service.show('删除车辆成功', { type: 'success' })
          // refresh current page
          await loadPage(page.value || 1)
        } else {
          service.show(resp && resp.message ? resp.message : '删除失败', { type: 'error' })
        }
      } catch (err) {
        console.error('removeVehicle error', err)
        const msg = err?.response?.data?.message || err.message || '删除失败'
        service.show(msg, { type: 'error' })
      } finally {
        deleting.value = false
      }
    }

    onMounted(() => { loadPage(1) })

    return { vehicles, loading, error, page, pageSize, total, totalPages, paged, lpFilter, vtypeFilter,
      loadPage, openAdd, applyFilters, clearFilters, onPageSizeChange, openHistory, transferTo, removeVehicle,
      showAdd, newVehicle, adding, createVehicle, closeAdd,
      // delete bindings
      deleting,
      // transfer modal bindings
      showTransfer, transferring, transferTarget, transferForm, confirmTransfer, cancelTransfer,
      // history modal bindings
      showHistory, historyLoading, historyList, historyTarget, closeHistory,
      // helpers
      formatDate }
  }
}
</script>

<style scoped>
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.controls input { padding:6px; margin-right:6px }
.vehicles-table { width:100%; border-collapse: collapse }
.vehicles-table th, .vehicles-table td { padding:8px; border:1px solid #eee; text-align:left }
.pagination { margin-top:12px; display:flex; gap:8px; align-items:center }
.loading { padding:20px }
.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:50 }
.modal { background:#fff; padding:16px; border-radius:6px; width:320px; box-shadow:0 6px 18px rgba(0,0,0,0.2) }
.modal label { display:block; margin:8px 0 }
.modal-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:12px }
.readonly-field { padding:6px 8px; background:#f6f6f6; border:1px solid #eee; border-radius:4px }
.danger { background:#ef4444; color:#fff; border:none; padding:6px 8px; border-radius:4px }

.history-table { width:100%; border-collapse: collapse; margin-top:8px; table-layout: fixed }
.history-table th, .history-table td { padding:8px; border:1px solid #e6e6e6; text-align:left; vertical-align:top }
.history-table thead th { background:#f3f4f6; font-weight:600 }
.history-table tbody tr:nth-child(odd) { background:#fff }
.history-table th:nth-child(1), .history-table td:nth-child(1) { width:10% }
.history-table th:nth-child(2), .history-table td:nth-child(2) { width:10% }
.history-table th:nth-child(3), .history-table td:nth-child(3) { width:20% }
.history-table th:nth-child(4), .history-table td:nth-child(4) { width:60% }
.history-table td.note-cell { white-space:normal; word-break:break-word }
.history-table td.date-cell { white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.history-modal .modal-actions { justify-content:flex-end; margin-top:12px }
</style>
