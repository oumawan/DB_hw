<template>
  <div class="admin-schedules">
    <header class="toolbar">
      <h2>班次管理</h2>
      <div class="controls">
      </div>
    </header>

    <section class="filters">
      <label>按类型
        <select v-model="mode">
          <option value="line">按线路</option>
          <option value="vehicle">按车辆</option>
          <option value="driver">按司机</option>
        </select>
      </label>
      <label v-if="mode==='line'">线路 ID <input v-model="query" placeholder="填写 lineNo"/></label>
      <label v-if="mode==='vehicle'">车辆 VID <input v-model="query" placeholder="填写 vid"/></label>
      <label v-if="mode==='driver'">司机 UID <input v-model="query" placeholder="填写 uid"/></label>
      <div class="filter-actions">
        <button @click="applyFilters">查询</button>
        <button @click="clearFilters">清除</button>
      </div>
    </section>

    <div class="dispatch">
      <h3>自动分配班次</h3>
      <label>线路 ID <input v-model="dispatch.lineNo" @input="updatePredictedAtime"/></label>
      <label>出发时间 <input type="datetime-local" v-model="dispatch.dtime" :min="minDtime" @input="updatePredictedAtime"/></label>
      <label>预计到达 <span class="readonly-field nowrap">{{ predictedAtime || '-' }}</span></label>
      <div class="modal-actions">
        <button @click="autoDispatch" :disabled="dispatching">自动签派</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <table class="lines-table">
        <thead>
          <tr>
            <th>SID</th>
            <th>出发时间</th>
            <th>到达时间</th>
            <th>起点/地点</th>
            <th>线路</th>
            <th>车辆</th>
            <th>司机</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in schedules" :key="s.sid">
            <td>{{ s.sid }}</td>
            <td class="nowrap">{{ new Date(s.dtime).toLocaleString() }}</td>
            <td class="nowrap">{{ new Date(s.atime).toLocaleString() }}</td>
            <td>{{ s.dlocation || '-' }}</td>
            <td>{{ s.lineNo || s.lineNo_id || '-' }}</td>
            <td>{{ s.vid || s.vid_id || '-' }}</td>
            <td>{{ s.uid || s.uid_id || '-' }}</td>
          </tr>
          <tr v-if="schedules.length===0"><td colspan="7">暂无班次</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { apiService } from '@/api/api.js'
import service from '@/plugins/messageService'
import { getUserFromLocal } from '@/plugins/storage'

export default {
  name: 'AdminSchedules',
  setup() {
    const mode = ref('line')
    const query = ref('')
    const loading = ref(false)
    const schedules = ref([])

    const dispatch = ref({ lineNo: '', dtime: '', atime: '' })
    const dispatching = ref(false)
    const predictedAtime = ref('')
    const _predictTimer = ref(null)
    const minDtime = ref('')
    const _minTimer = ref(null)

    function pad(n){ return (n<10? '0':'')+n }
    function formatDate(v){ if(!v) return ''; try { const d=new Date(v); if(isNaN(d.getTime())) return v; return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` } catch(e){ return v } }

    function getNowForInput(){ const d=new Date(); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}` }

    async function load() {
      loading.value = true
      schedules.value = []
      try {
        const user = getUserFromLocal() || {}
        const depotID = user.depotID || null
        let res
        // if no query provided, fetch all schedules for this depot
        if (!query.value || String(query.value).trim() === '') {
          res = await apiService.fetchAllSchedules({ depotID })
        } else if (mode.value === 'line') {
          res = await apiService.fetchSchedulesByLine({ lineNo: query.value, depotID })
        } else if (mode.value === 'vehicle') {
          res = await apiService.fetchSchedulesByVehicle({ vid: query.value, depotID })
        } else {
          res = await apiService.fetchSchedulesByDriver({ uid: query.value, depotID })
        }
        if (res && res.success) {
          // responses use key 'schedules'
          const normalizeServerTime = (v) => {
            if (!v) return v
            if (typeof v !== 'string') return v
            // already has timezone info (Z or +hh:mm)
            if (v.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(v)) return v
            // ISO without tz (e.g. 2025-12-16T10:00:00) or space separated (2025-12-16 10:00:00)
            // treat backend-naive timestamps as UTC and append 'Z' so browser parses correctly
            return v.replace(' ', 'T') + 'Z'
          }
          schedules.value = (res.schedules || []).map(s => ({
            ...s,
            dtime: normalizeServerTime(s.dtime),
            atime: normalizeServerTime(s.atime)
          }))
        } else {
          service.show(res && res.message ? res.message : '查询失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('查询失败', { type: 'error' })
      } finally {
        loading.value = false
      }
    }

    function applyFilters(){ load() }
    function clearFilters(){ query.value=''; load() }

    async function autoDispatch(){
      if (!dispatch.value.lineNo || !dispatch.value.dtime) { service.show('请填写正确的线路号或出发时间', { type: 'warning' }); return }

      // 不允许选择过去时间（前端二次校验）
      const picked = new Date(dispatch.value.dtime)
      if (isNaN(picked.getTime()) || picked.getTime() < Date.now()) {
        service.show('出发时间不能早于当前时间', { type: 'warning' }); return
      }

      // 要求前端必须已有 atime（ISO），否则直接拒绝签派
      if (!dispatch.value.atime) {
        service.show('请填写正确的线路号或时间', { type: 'warning' })
        return
      }
      const atCheck = new Date(dispatch.value.atime)
      if (isNaN(atCheck.getTime())) {
        service.show('预计到达时间无效', { type: 'warning' })
        return
      }

      dispatching.value = true
      try {
        const dtimeISO = new Date(dispatch.value.dtime).toISOString()
        const atimeISO = new Date(dispatch.value.atime).toISOString()
        const user = getUserFromLocal()
        const depotID = user.depotID || null
        const res = await apiService.autoDispatchSchedule({ lineNo: dispatch.value.lineNo, dtime: dtimeISO, atime: atimeISO, depotID: depotID })
        if (res && res.success) {
          service.show('自动签派成功', { type: 'success' })
          load()
        } else {
          service.show(res && res.message ? res.message : '自动签派失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        const message = err?.response?.data?.message || '失败'
        service.show(message, { type: 'error' })
      } finally {
        dispatching.value = false
      }
    }

    async function updatePredictedAtime(){
      // cancel any pending timer
      if (_predictTimer.value) { clearTimeout(_predictTimer.value); _predictTimer.value = null }
      predictedAtime.value = ''
      // clear previous atime to avoid stale usage while computing
      dispatch.value.atime = ''
      if (!dispatch.value.lineNo || !dispatch.value.dtime) return
      try {
        const user = getUserFromLocal() || {}
        const depotID = user.depotID || null
        const lr = await apiService.fetchOneLineRunDuration({ lineNo: dispatch.value.lineNo, depotID })
        if (!lr || lr.success === false) return
        let runDur = null
        if (typeof lr.run_duration !== 'undefined') runDur = lr.run_duration
        else if (lr.line && typeof lr.line.run_duration !== 'undefined') runDur = lr.line.run_duration
        if (runDur === null || runDur === undefined) return
        const start = new Date(dispatch.value.dtime)
        if (isNaN(start.getTime())) return
        const atime = new Date(start.getTime() + Number(runDur) * 60000)
        predictedAtime.value = formatDate(atime.toISOString())
        // persist ISO into dispatch.atime so autoDispatch can use it directly
        dispatch.value.atime = atime.toISOString()
      } catch (e) {
        // silent
      }
    }

    // keep minDtime updated (so picker disables past minutes while page is open)
    minDtime.value = getNowForInput()
    _minTimer.value = setInterval(() => { minDtime.value = getNowForInput() }, 30*1000)
    onUnmounted(() => { if (_minTimer.value) clearInterval(_minTimer.value) })

    // watch for changes and debounce recomputation to avoid race conditions
    watch(() => [dispatch.value.lineNo, dispatch.value.dtime], () => {
      // clear displayed prediction and stored atime immediately to avoid stale use
      predictedAtime.value = ''
      dispatch.value.atime = ''
      if (_predictTimer.value) clearTimeout(_predictTimer.value)
      // schedule recompute after brief debounce
      _predictTimer.value = setTimeout(() => {
        updatePredictedAtime()
        _predictTimer.value = null
      }, 300)
    })

    onMounted(()=> load())

    // watch dispatch inputs to update predictedAtime (lightweight: manual call on input)
    // add small helper: caller can call updatePredictedAtime() when inputs change

    return { mode, query, loading, schedules, formatDate, applyFilters, clearFilters, dispatch, autoDispatch, dispatching, predictedAtime, updatePredictedAtime, minDtime }
  }
}
</script>

<style scoped>
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.filters { display:flex; gap:12px; align-items:center; margin-bottom:12px }
.filters label { display:flex; gap:8px; align-items:center }
.lines-table { width:100%; border-collapse:collapse; margin-top:12px }
.lines-table th, .lines-table td { padding:8px; border:1px solid #eee; text-align:left }
.dispatch { margin-top:16px; padding:12px; border:1px solid #eee; border-radius:6px; background:#fafafa }
.modal-actions { margin-top:8px }
.nowrap { white-space: nowrap }
</style>
