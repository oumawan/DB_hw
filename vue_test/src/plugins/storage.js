export function saveUserToLocal(user) {
    const payload = {
        uid: user.uid,
        email: user.email,
        name: user.name,
        is_admin: user.is_admin,
        depotID: user.depotID,
        license: user.license || null,
        saved_at: new Date().toISOString()
    }
    sessionStorage.setItem('user', JSON.stringify(payload))
    sessionStorage.setItem('loggedIn', 'true')
    sessionStorage.setItem('isAdmin', user.is_admin ? 'true' : 'false')
}

export function getUserFromLocal() {
    const userStr = sessionStorage.getItem('user')
    if (!userStr) return null
    try {
        const user = JSON.parse(userStr)
        return user
    } catch (e) {
        console.error('Error parsing user from localStorage', e)
        clearUserFromLocal()
        return null
    }
}

export function clearUserFromLocal() {
    sessionStorage.removeItem('user')
    sessionStorage.setItem('loggedIn', 'false')
    sessionStorage.removeItem('isAdmin')
}