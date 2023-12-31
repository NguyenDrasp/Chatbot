import axiosInstance from "./axiosInstance"
import useSWR from "swr"

export const saveHistory = async (payload: {
  session_id: string
  history: string
}) => {
  return await axiosInstance.post("/save_history/", payload, {
    baseURL: process.env.NEXT_PUBLIC_URL
  })
}