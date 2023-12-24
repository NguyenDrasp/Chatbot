import { SignUpForm } from "@/pages/sign-up"
import axiosInstance from './axiosInstance';

export const signUp = async (form: SignUpForm) => {
  return await axiosInstance.post("/api/users/", form, {
    baseURL: process.env.NEXT_PUBLIC_AUTH
  })
}
