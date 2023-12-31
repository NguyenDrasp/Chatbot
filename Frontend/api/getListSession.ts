import axiosInstance from "./axiosInstance"
import useSWR from "swr"

const getListSession = async (userId: string) => {
  return await axiosInstance.post(
    "/list_session/",
    { user_id: userId },
    {
      baseURL: process.env.NEXT_PUBLIC_URL
    }
  )
}

export const useGetListSession = (userId: string, sessionId: string | null) => {
  const { data, isLoading, error } = useSWR(
    userId ? userId + sessionId : null,
    () => getListSession(userId)
  )
  return { data, isLoading, status: error?.response?.status }
}
