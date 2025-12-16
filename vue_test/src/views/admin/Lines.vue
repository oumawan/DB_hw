<template>
  <div class="admin-lines">
    <header class="toolbar">
      <h2>线路管理</h2>
      <div class="controls">
        <button @click="openAdd">添加线路</button>
      </div>
    </header>

    <section class="filters">
      <label>线路名称 <input v-model="nameFilter" placeholder="按名称搜索"/></label>
      <label>站点名称 <input v-model="stationFilter" placeholder="起点或终点包含"/></label>
      <div class="filter-actions">
        <button @click="applyFilters">应用筛选</button>
        <button @click="clearFilters">清除筛选</button>
      </div>
    </section>

    <div v-if="loading" class="loading">加载中…</div>
    <div v-else>
      <table class="lines-table">
        <thead>
          <tr><th>线路ID</th><th>名称</th><th>起点</th><th>终点</th><th>车型</th><th>运行时长(小时:分钟)</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="line in paged" :key="line.lid">
            <td>{{ line.lid }}</td>
            <td>{{ line.name }}</td>
            <td>{{ line.from }}</td>
            <td>{{ line.to }}</td>
            <td>{{ line.vtype || '-' }}</td>
            <td>{{ formatDuration(line.run_duration) }}</td>
            <td>
              <button @click.prevent="removeLine(line)" class="danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page<=1" @click="loadPage(1)">« 首页</button>
        <button :disabled="page<=1" @click="loadPage(page-1)">‹ 上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
        <button :disabled="page>=totalPages" @click="loadPage(page+1)">下一页 ›</button>
        <button :disabled="page>=totalPages" @click="loadPage(totalPages)">末页 »</button>
      </div>
    </div>

    <!-- Add Line Modal -->
    <div v-if="showAdd" class="modal-overlay">
      <div class="modal">
        <h3>添加线路</h3>
        <label>名称 <input v-model="newLine.lineName" placeholder="线路名称"/></label>
        <label>起点 <input v-model="newLine.lineFrom" placeholder="起始站点"/></label>
        <label>终点 <input v-model="newLine.lineTo" placeholder="终点站点"/></label>
        <label>车型
          <select v-model="newLine.vtype">
            <option value="">请选择车型（可选）</option>
            <option>大型客车</option>
            <option>重型牵引挂车</option>
            <option>城市公交车</option>
            <option>中型客车</option>
            <option>大型货车</option>
            <option>小型汽车</option>
            <option>小型自动挡汽车</option>
          </select>
        </label>
        <label>运行时长（小时:分钟） <input v-model="newLine.run_duration_str" placeholder="例如 1:30 或 90（分钟）"/></label>
        <div class="modal-actions">
          <button @click="createLine" :disabled="adding">添加</button>
          <button @click="closeAdd" :disabled="adding">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import service from '@/plugins/messageService'
import { apiService } from '@/api/api.js'
import { getUserFromLocal } from '@/plugins/storage'

export default {
  name: 'AdminLines',
  setup() {
    const lines = ref([])
    const loading = ref(false)
    const page = ref(1)
    const pageSize = ref(10)
    const total = ref(0)

    const nameFilter = ref('')
    const stationFilter = ref('')

    const showAdd = ref(false)
    const adding = ref(false)
    const newLine = ref({ lineName: '', lineFrom: '', lineTo: '', vtype: '', run_duration: null, run_duration_str: '' })

    const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
    const paged = computed(() => {
      const p = Math.max(1, Number(page.value) || 1)
      const ps = Math.max(1, Number(pageSize.value) || 10)
      const start = (p-1)*ps
      return lines.value.slice(start, start+ps)
    })

    async function loadPage(p=1) {
      loading.value = true
      try {
        const user = getUserFromLocal() || {}
        const depotID = user.depotID || null
        const res = await apiService.fetchAllLines({ depotID })
        if (res && res.success && Array.isArray(res.lines)) {
          // map backend fields to frontend-friendly names
          lines.value = res.lines.map(l => ({
            lid: l.lineNo,
            name: l.lineName,
            from: l.lineFrom,
            to: l.lineTo,
            vtype: l.vtype,
            run_duration: l.run_duration
          }))

          // client-side filters
          let filtered = lines.value.slice()
          if (nameFilter.value && String(nameFilter.value).trim()) {
            const q = String(nameFilter.value).toLowerCase()
            filtered = filtered.filter(l => l.name && l.name.toLowerCase().includes(q))
          }
          if (stationFilter.value && String(stationFilter.value).trim()) {
            const q2 = String(stationFilter.value).toLowerCase()
            filtered = filtered.filter(l => (l.from && String(l.from).toLowerCase().includes(q2)) || (l.to && String(l.to).toLowerCase().includes(q2)))
          }
          lines.value = filtered
          total.value = lines.value.length
          page.value = p
        } else {
          service.show('加载线路失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('加载线路失败', { type: 'error' })
      } finally {
        loading.value = false
      }
    }

    function applyFilters() { page.value = 1; loadPage(1) }
    function clearFilters() { nameFilter.value = ''; stationFilter.value = ''; page.value = 1; loadPage(1) }
    function openAdd() { showAdd.value = true }
    function closeAdd() { showAdd.value = false; newLine.value = { lineName: '', lineFrom: '', lineTo: '', vtype: '', run_duration: null, run_duration_str: '' } }


    async function removeLine(l) {
      try {
        const ok = await service.showConfirm(`确定删除线路 ${l.name} 吗？`, {type: 'warning', confirmText: '删除', cancelText: '取消'})
        if (!ok) return
        const user = getUserFromLocal() || {}
        const depotID = user.depotID || null
        const res = await apiService.removeLine({ lineNo: l.lid, depotID })
        if (res && res.success) {
          service.show('删除成功', { type: 'success' })
          loadPage(page.value)
        } else {
          service.show(res.message || '删除失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('删除失败', { type: 'error' })
      }
    }

    function formatDuration(minutes) {
      if (minutes === null || minutes === undefined || minutes === '') return '-'
      const m = Number(minutes)
      if (isNaN(m)) return '-'
      const h = Math.floor(m / 60)
      const mm = m % 60
      return `${h}:${mm < 10 ? '0' + mm : mm}`
    }

    function parseDurationToMinutes(s) {
      if (s === null || s === undefined) return null
      const t = String(s).trim()
      if (t === '') return null
      const colonMatch = t.match(/^(\d+):(\d{1,2})$/)
      if (colonMatch) {
        const h = Number(colonMatch[1])
        const mm = Number(colonMatch[2])
        if (isNaN(h) || isNaN(mm) || mm < 0 || mm >= 60) return NaN
        return h * 60 + mm
      }
      if (/^\d+$/.test(t)) return Number(t)
      return NaN
    }

    async function createLine() {
      if (!newLine.value.lineName || !newLine.value.lineFrom || !newLine.value.lineTo) {
        service.show('请填写名称、起点和终点', { type: 'warning' })
        return
      }
      adding.value = true
      try {
        const user = getUserFromLocal() || {}
        const depotID = user.depotID || null
        // parse run_duration_str to minutes
        let runDur = null
        if (newLine.value.run_duration_str !== null && newLine.value.run_duration_str !== undefined && String(newLine.value.run_duration_str).trim() !== '') {
          const parsed = parseDurationToMinutes(newLine.value.run_duration_str)
          if (isNaN(parsed)) {
            service.show('运行时长格式错误，示例：1:30 或 90（分钟）', { type: 'warning' })
            adding.value = false
            return
          }
          runDur = parsed
        }

        const payload = {
          lineName: newLine.value.lineName,
          lineFrom: newLine.value.lineFrom,
          lineTo: newLine.value.lineTo,
          depotID: depotID,
          vtype: newLine.value.vtype || '',
          run_duration: runDur
        }
        const res = await apiService.addLine(payload)
        if (res && res.success) {
          service.show('添加线路成功', { type: 'success' })
          closeAdd()
          loadPage(1)
        } else {
          service.show(res.message || '添加失败', { type: 'error' })
        }
      } catch (err) {
        console.error(err)
        service.show('添加失败', { type: 'error' })
      } finally {
        adding.value = false
      }
    }

    onMounted(()=> loadPage(1))

    return { lines, loading, page, pageSize, total, totalPages, paged, nameFilter, stationFilter, loadPage, applyFilters, clearFilters, openAdd, closeAdd, showAdd, newLine, createLine, adding, removeLine, formatDuration }
  }
}
</script>

<style scoped>
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.lines-table { width:100%; border-collapse:collapse }
.lines-table th, .lines-table td { padding:8px; border:1px solid #eee; text-align:left }
.pagination { margin-top:12px; display:flex; gap:8px; align-items:center }
.danger { background:#ef4444; color:#fff; border:none; padding:6px 8px; border-radius:4px }

/* modal */
.modal-overlay { position:fixed; left:0; top:0; right:0; bottom:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center }
.modal { background:#fff; padding:16px; border-radius:6px; min-width:320px; box-shadow:0 6px 20px rgba(0,0,0,0.2) }
.modal label { display:block; margin:8px 0 }
.modal input { width:100%; padding:6px; box-sizing:border-box }
.modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:12px }
</style>
