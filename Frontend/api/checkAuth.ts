import axiosInstance from "./axiosInstance"
import useSWR from "swr"

const checkAuth = async () => {
  //   try {
  //     const { data, status } = await axiosInstance.get("/api/users/me/", {
  //       baseURL: process.env.NEXT_PUBLIC_AUTH
  //     })
  //     return { data, status }
  //   } catch (error) {
  //     // Handle the error here
  //     return {error }
  //   }
  return await axiosInstance.get("/api/users/me/", {
    baseURL: process.env.NEXT_PUBLIC_AUTH
  })
}

export const useCheckAuth = () => {
  const { data, isLoading, error } = useSWR("/api/users/me/", checkAuth)
  return { data, isLoading, status: error?.response?.status }
}
