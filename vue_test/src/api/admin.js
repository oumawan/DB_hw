import api, { apiService } from './api.js'

/**
 * Admin API wrapper — calls real backend endpoints.
 * Keeps the same exported function names used by the UI.
 *
 * Note: backend must implement the corresponding endpoints. If an apiService
 * helper exists (named export in `api.js`) we use it first, falling back to
 * raw `api` axios calls.
 */


export async function fetchDrivers({ page = 1, page_size = 10, search = '', name = '', uid = '', email = '', license = '', depotID = '' } = {}) {
  try {
    // prefer apiService.fetchAllDrivers if available
    let raw = await apiService.fetchAllDrivers({ depotID })
    if (raw && raw.success === false) {
      return raw
    }
    const list = raw.drivers
    // apply client-side filtering (keeps compatibility with previous behaviour)
    let filtered = list.slice()
    if (search && String(search).trim()) {
      const q = String(search).toLowerCase()
      filtered = filtered.filter(d => (
        (d.name && d.name.toLowerCase().includes(q)) ||
        (d.email && d.email.toLowerCase().includes(q)) ||
        (d.uid && String(d.uid).toLowerCase().includes(q))
      ))
    }
    if (name && String(name).trim()) {
      const q = String(name).toLowerCase()
      filtered = filtered.filter(d => d.name && d.name.toLowerCase().includes(q))
    }
    if (uid && String(uid).trim()) {
      const q = String(uid).toLowerCase()
      filtered = filtered.filter(d => d.uid && String(d.uid).toLowerCase().includes(q))
    }
    if (email && String(email).trim()) {
      const q = String(email).toLowerCase()
      filtered = filtered.filter(d => d.email && d.email.toLowerCase().includes(q))
    }
    if (license && String(license).trim()) {
      const q = String(license).toLowerCase()
      filtered = filtered.filter(d => d.license && d.license.toLowerCase() === q)
    }

    const total = filtered.length
    const p = Math.max(1, Number(page) || 1)
    const ps = Math.max(1, Number(page_size) || 10)
    const start = (p - 1) * ps
    const results = filtered.slice(start, start + ps)

    return { data: { results, total, page: p, page_size: ps } }
  } catch (err) {
    // bubble up error for caller to handle
    return { message: "Error fetching drivers: " + err.message }
  }
}

export async function fetchDriver(uid) {
  try {
    return await apiService.fetchDriver(uid)
  } catch (err) {
    return { message: "Error fetching driver: " + err.message}
  }
}

export async function createDriver(payload) {
  return await apiService.createDriver(payload)
}

export async function updateDriver(uid, payload) {
  try {
    if (apiService && typeof apiService.updateDriver === 'function') {
      return await apiService.updateDriver(uid, payload)
    }
    const resp = await api.post('/api/admin/updateDriver', Object.assign({ uid }, payload))
    return resp.data
  } catch (err) {
    return { message: "Error updating driver: " + err.message }
  }
}

export async function deleteDriver(uid) {
  try {
    if (apiService && typeof apiService.deleteDriver === 'function') {
      return await apiService.deleteDriver(uid)
    }
    const resp = await api.post('/api/admin/deleteDriver', { uid })
    return resp.data
  } catch (err) {
    return { message: "Error deleting driver: " + err.message}
  }
}

export default {
  fetchDrivers,
  fetchDriver,
  createDriver,
  updateDriver,
  deleteDriver
}
