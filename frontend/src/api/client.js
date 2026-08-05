const BASE_URL = import.meta.env.VITE_API_URL

function getToken() {
  return localStorage.getItem("token")
}

export function setToken(token) {
  localStorage.setItem("token", token)
}

export function clearToken() {
  localStorage.removeItem("token")
}

async function request(path, options = {}) {
  const token = getToken()

  const headers = { "Content-Type": "application/json", ...options.headers }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (response.status === 401) {
    clearToken()
    window.location.href = "/login"
    return
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const code = data?.detail?.code || "UNKNOWN_ERROR"
    const error = new Error(code)
    error.code = code
    error.data = data?.detail
    throw error
  }

  return data
}

export function get(path) {
  return request(path)
}

export function post(path, body) {
  return request(path, { method: "POST", body: JSON.stringify(body) })
}

export function put(path, body) {
  return request(path, { method: "PUT", body: JSON.stringify(body) })
}