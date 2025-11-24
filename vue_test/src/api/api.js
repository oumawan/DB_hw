import axios from 'axios'

const api = axios.create(
    {
        baseURL: 'http://localhost:8000',
        timeout: 5000
    }
)

export const apiService = {
    async login(credentials) {
        const response = await api.post('/api/login/', credentials)
        return response.data
    },

    async driver_change_profile(data) {
        const response = await api.post("/api/drivers/changeProfile", data)
        return response.data
    },

    async fetchAllDrivers(depotID) {
        const response = await api.post("/api/admin/fetchAllDrivers", depotID)
        return response.data
    },

    async createDriver(driverData) {
        const response = await api.post("/api/admin/createDriver", driverData)
        return response.data
    }
}
export default api