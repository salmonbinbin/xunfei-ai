import api from './index'

export function login(data) {
  return api.post('/auth/login', data)
}

export function register(data) {
  return api.post('/auth/register', data)
}

export function updateProfile(data) {
  return api.post('/auth/profile', data)
}

export function getCurrentUser() {
  return api.get('/auth/me')
}
