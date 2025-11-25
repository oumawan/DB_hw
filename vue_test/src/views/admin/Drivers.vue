<template>
  <div class="admin-drivers">
    <header class="toolbar">
      <h2>司机管理</h2>
      <div class="controls">
        <button @click="openAdd">添加司机</button>
      </div>
    </header>

    <section class="filters">
      <label>姓名 <input v-model="nameFilter" placeholder="按姓名搜索" /></label>
      <label>编号 <input v-model="uidFilter" placeholder="按编号搜索" /></label>
      <label>邮箱 <input v-model="emailFilter" placeholder="按邮箱搜索" /></label>
      <label>准驾
        <select v-model="licenseFilter">
          <option value="">全部</option>
          <option value="A1">A1</option>
          <option value="B1">B1</option>
          <option value="C1">C1</option>
        </select>
      </label>
      <!-- 车场由管理员身份决定，移除页面筛选控件 -->
      <div class="filter-actions">
        <button @click="applyFilters">应用筛选</button>
        <button @click="clearFilters">清除筛选</button>
      </div>
    </section>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <!-- Add Driver Modal -->
      <div v-if="showAdd" class="modal-backdrop">
        <div class="modal">
          <h3>添加司机</h3>
          <label>姓名 <input v-model="newDriver.name" /></label>
          <label>邮箱 <input v-model="newDriver.email" /></label>
          <label>准驾
            <select v-model="newDriver.license">
              <option value="">请选择</option>
              <option value="A1">A1</option>
              <option value="B1">B1</option>
              <option value="C1">C1</option>
            </select>
          </label>
          <label>车场
            <!-- depot is fixed to admin's depot / current depotFilter and cannot be changed here -->
            <div class="readonly-field">{{ newDriver.depotID || (depotFilter || '未指定') }}</div>
          </label>
          <div class="modal-actions">
            <button @click="createDriver">保存</button>
            <button @click="closeAdd">取消</button>
          </div>
        </div>
      </div>
      <table class="drivers-table">
        <thead>
          <tr>
            <th>编号</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>准驾车型</th>
            <th>车场</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in drivers" :key="d.uid">
            <td>{{ d.uid }}</td>
            <td>{{ d.name }}</td>
            <td>{{ d.email }}</td>
            <td>{{ d.license }}</td>
            <td>{{ d.depotID }}</td>
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
import api from '../../api/admin'
import service from '../../plugins/messageService'
import { getUserFromLocal } from '../../plugins/storage'

export default {
  name: 'AdminDrivers',
  setup() {
    const drivers = ref([])
    const loading = ref(false)
    const error = ref(null)
    const page = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    // attribute filters
    const nameFilter = ref('')
    const uidFilter = ref('')
    const emailFilter = ref('')
    const licenseFilter = ref('')
    // depot is determined from current admin user
    const showAdd = ref(false)
    const newDriver = ref({ name: '', email: '', license: '', depotID: '' })

    const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

    function formatDate(s) {
      if (!s) return '-'
      try { return new Date(s).toLocaleString() } catch (e) { return s }
    }

    async function loadPage(p = 1) {
      loading.value = true
      error.value = null
      try {
          const user = getUserFromLocal()
          const adminDepot = (user && user.depotID) ? user.depotID : ''
          const res = await api.fetchDrivers({
          page: p,
          page_size: pageSize.value,
          name: nameFilter.value,
          uid: uidFilter.value,
          email: emailFilter.value,
          license: licenseFilter.value,
          depotID: adminDepot
        })
        if (res.success == false) {
          service.show('加载司机列表失败: ' + (res.message || '未知错误'), { type: 'error' })
          loading.value = false
          return
        } else {
          const data = res.data
          const results = (data.results || []).map(d => ({ depotID: d.depotID || adminDepot, ...d }))
          drivers.value = results
          total.value = data.total || 0
          page.value = data.page || p
        }
      } catch (err) {
        error.value = err
        service.show('加载司机列表失败', { type: 'error' })
      } finally {
        loading.value = false
      }
    }

    function openAdd() {
      // prefer depot stored on current admin user; fallback to depotFilter
      const user = getUserFromLocal()
      const adminDepot = (user && user.depotID) ? user.depotID : ''
      newDriver.value = { name: '', email: '', license: '', depotID: adminDepot }
      showAdd.value = true
    }

    function closeAdd() {
      showAdd.value = false
    }

    async function createDriver() {
      // basic validation
      if (!newDriver.value.name || !newDriver.value.email) {
        service.show('请填写姓名和邮箱', { type: 'error' })
        return
      }
      // ensure depot is present: prefer admin's depot from localStorage, fallback to depotFilter
      if (!newDriver.value.depotID) {
        const user2 = getUserFromLocal()
        if (user2 && user2.depotID) {
          newDriver.value.depotID = user2.depotID
        } else {
          service.show('车场信息缺失，无法添加', { type: 'error' })
          return
        }
      }
      loading.value = true
      try {
        const response = await api.createDriver(Object.assign({}, newDriver.value))
        if (response.success) {
          service.show('添加成功', { type: 'success' })
        } else {
          service.show(response.message || '添加失败', { type: 'error' })
          return
        }
        // reload current page to reflect changes
        await loadPage(page.value)
        showAdd.value = false
      } catch (err) {
        console.error('createDriver error', err)
        service.show('添加失败', { type: 'error' })
      } finally {
        loading.value = false
      }
    }

    

    function applyFilters() {
      loadPage(1)
    }

    function clearFilters() {
      nameFilter.value = ''
      uidFilter.value = ''
      emailFilter.value = ''
      licenseFilter.value = ''
      loadPage(1)
    }

    function onPageSizeChange() {
      loadPage(1)
    }

    onMounted(() => { loadPage(1) })

    return { drivers, loading, error, page, pageSize, total, totalPages, loadPage, onPageSizeChange, formatDate,
      nameFilter, uidFilter, emailFilter, licenseFilter,  applyFilters, clearFilters,
      showAdd, newDriver, openAdd, closeAdd, createDriver }
  }
}
</script>

<style scoped>
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
.controls input { padding:6px; margin-right:6px }
.drivers-table { width:100%; border-collapse: collapse }
.drivers-table th, .drivers-table td { padding:8px; border:1px solid #eee; text-align:left }
.pagination { margin-top:12px; display:flex; gap:8px; align-items:center }
.loading { padding:20px }
.modal-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:50 }
.modal { background:#fff; padding:16px; border-radius:6px; width:320px; box-shadow:0 6px 18px rgba(0,0,0,0.2) }
.modal label { display:block; margin:8px 0 }
.modal-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:12px }
.readonly-field { padding:6px 8px; background:#f6f6f6; border:1px solid #eee; border-radius:4px }
</style>
