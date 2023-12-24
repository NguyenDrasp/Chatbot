import axios from "axios"
const axiosInstance = axios.create()

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    // Modify the request config here (e.g., add headers, authentication tokens)
    if (config.url === "/api/users/" || config.url === "/api/jwt/create/") {
      return config
    }
    const accessToken = localStorage.getItem("access_token")

    // ** If token is present add it to request's Authorization Header
    if (accessToken) {
      if (config.headers) config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    // Handle request errors here

    return Promise.reject(error)
  }
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    // Modify the response data here (e.g., parse, transform)

    return response
  },
  (error) => {
    // Handle response errors here

    return Promise.reject(error)
  }
)

export default axiosInstance
