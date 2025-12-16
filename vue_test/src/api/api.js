import axios from 'axios'

const api = axios.create(
    {
        baseURL: 'http://localhost:8000',
        timeout: 5000
    }
)

export const apiService = {
    async login(request) {
        const response = await api.post('api/user/login/', request)
        return response.data
    },

    async driver_change_profile(request) {
        await api.post("api/user/changeProfile/", request)
        await api.post("api/driver/changeInfo/", request)
        return
    },

    async fetchAllDrivers(request) {
        const response = await api.post("api/admin/drivers/fetchAll/", request)
        return response.data
    },

    async createDriver(request) {
        const response = await api.post("api/admin/drivers/add/", request)
        return response.data
    },

    async modifyPassword(request) {
        const response = await api.post("api/user/modifyPassword/", request)
        return response.data
    },

    async fetchAllVehicles(request) {
        const response = await api.post("api/admin/vehicle/fetchAll/", request)
        return response.data
    }
,
    async fetchAllLines(request) {
        const response = await api.post("api/admin/line/fetchAll/", request)
        return response.data
    },
    async addVehicle(request) {
        const response = await api.post("api/admin/vehicle/add/", request)
        return response.data
    },

    async removeVehicle(request) {
        const response = await api.post("api/admin/vehicle/remove/", request)
        return response.data
    },

    async transferVehicle(request) {
        const response = await api.post("api/admin/vehicle/transfer/", request)
        return response.data
    },

    async fetchAllTransferHistory(request) {
        const response = await api.post("api/admin/vehicle/fetchAlltransferHistory/", request)
        return response.data
    },

    async addLine(request) {
        const response = await api.post("api/admin/line/add/", request)
        return response.data
    },

    async addLeave(request) {
        const response = await api.post("api/driver/leave/add/", request)
        return response.data
    },

    async removeLine(request) {
        const response = await api.post("api/admin/line/remove/", request)
        return response.data
    }
    ,
    async fetchSchedulesByLine(request) {
        const response = await api.post('api/schedules/byLine/', request)
        return response.data
    },
    async fetchAllSchedules(request) {
        const response = await api.post('api/schedules/fetchAll/', request)
        return response.data
    },
    async fetchSchedulesByVehicle(request) {
        const response = await api.post('api/schedules/byVehicle/', request)
        return response.data
    },
    async fetchSchedulesByDriver(request) {
        const response = await api.post('api/schedules/byDriver/', request)
        return response.data
    },
    async autoDispatchSchedule(request) {
        const response = await api.post('api/schedule/autoDispatch/', request)
        return response.data
    },

    async fetchOneLineRunDuration(request) {
        const response = await api.post('api/line/fetchOneRunDuration/', request)
        return response.data
    }
}
export default api