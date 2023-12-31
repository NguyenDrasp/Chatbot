import axiosInstance from "./axiosInstance"
import useSWR from "swr"

export const newSession = async (userId: string) => {
  return await axiosInstance.post(
    "/new_session/",
    {
      user_id: userId
    },
    {
      baseURL: process.env.NEXT_PUBLIC_URL
    }
  )
}