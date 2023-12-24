import { SignInForm } from "@/pages/sign-in";
import axiosInstance from './axiosInstance';

export const signIn = async (form: SignInForm) => {
  return await axiosInstance.post("/api/jwt/create/", form, {
    baseURL: process.env.NEXT_PUBLIC_AUTH
  })
}
