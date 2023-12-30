import axiosInstance from "./axiosInstance"
import useSWR from "swr"

export const getOldSessionHistory = async (sessionId: string) => {
  return await axiosInstance.post(
    "/old_session/",
    {
      session_id: sessionId
    },
    {
      baseURL: process.env.NEXT_PUBLIC_URL
    }
  )
}

export const useGetOldHistory = (sessionId: string | null) => {
  const { data, isLoading, error } = useSWR(sessionId ? sessionId : null, () =>
    getOldSessionHistory(sessionId as string)
  )
  return { data, isLoading, status: error?.response?.status }
}
