import api from './index'

export function teacherLogin(data) {
  return api.post('/auth/teacher/login', data)
}

export function teacherRegister(data) {
  return api.post('/auth/teacher/register', data)
}
