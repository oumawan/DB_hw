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
    localStorage.setItem('user', JSON.stringify(payload))
    localStorage.setItem('loggedIn', 'true')
    localStorage.setItem('isAdmin', user.is_admin ? 'true' : 'false')
}

export function getUserFromLocal() {
    const userStr = localStorage.getItem('user')
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
    localStorage.removeItem('user')
    localStorage.setItem('loggedIn', 'false')
    localStorage.removeItem('isAdmin')
}