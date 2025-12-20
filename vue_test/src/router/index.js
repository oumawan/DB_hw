import {createRouter, createWebHistory} from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import MainPage from '../views/MainPage.vue'
import AdminPage from '../views/admin/AdminPage.vue'
import AdminDrivers from '../views/admin/Drivers.vue'
import AdminVehicles from '../views/admin/Vehicles.vue'
import AdminSchedules from '../views/admin/Schedules.vue'
import AdminLeaves from '../views/admin/Leaves.vue'
import AdminLines from '../views/admin/Lines.vue'
import DriverProfile from '../views/driver/DriverProfile.vue'
import DriverPage from '../views/driver/DriverPage.vue'
import DriverSchedules from '../views/driver/Schedules.vue'
import DriverLeaves from '../views/driver/Leaves.vue'
const routes = [
    { path: '/', component: LoginPage, meta: { title: 'Login' } },
    { path: '/main', component: MainPage, meta: { title: 'Main', requiresAuth: true } },
    {
        path: '/driver',
        component: DriverPage,
        meta: { title: 'Driver' },
        children: [
            { path: '', redirect: '/driver/profile' },
            { path: 'profile', component: DriverProfile, meta: { title: '个人信息' } },
            { path: 'schedules', component: DriverSchedules, meta: { title: '我的班次' } },
            { path: 'leaves', component: DriverLeaves, meta: { title: '请假申请' } },
            
        ]
    },
    {
        path: '/admin',
        component: AdminPage,
        meta: { title: 'Admin' },
        children: [
            { path: '', redirect: '/admin/drivers' },
            { path: 'drivers', component: AdminDrivers, meta: { title: '司机管理' } },
            { path: 'vehicles', component: AdminVehicles, meta: { title: '车辆管理' } },
            { path: 'schedules', component: AdminSchedules, meta: { title: '班次管理' } },
            { path: 'lines', component: AdminLines, meta: { title: '线路管理' } },
            { path: 'leaves', component: AdminLeaves, meta: { title: '请假管理' } }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    document.title = to.meta.title || 'Vue App'
    // simple auth & role guard: check localStorage flags set on successful login
    const logged = sessionStorage.getItem('loggedIn') === 'true'
    const isAdmin = sessionStorage.getItem("isAdmin") === 'true'

    // not logged in -> only allow login page
    if (!logged) {
        if (to.path === '/' ) return next()
        return next({ path: '/' })
    }

    // logged in -> if user goes to root, redirect to their home
    if (to.path === '/') {
        return next({ path: isAdmin ? '/admin/drivers' : '/driver/profile' })
    }

    // Admin users: only allow /admin routes
    if (isAdmin) {
        if (to.path.startsWith('/admin')) return next()
        return next({ path: '/admin/drivers' })
    }

    // Non-admin (driver) users: only allow /driver routes
    if (to.path.startsWith('/driver')) return next()
    return next({ path: '/driver/profile' })
})

export default router