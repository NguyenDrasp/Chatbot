import { signUp } from "@/api/signUp"
import { useRouter } from "next/navigation"
import React, { useState } from "react"

type Props = {}

export type SignUpForm = {
  first_name: ""
  last_name: ""
  email: ""
  password: ""
  re_password: ""
}

const SignUp = (props: Props) => {
  const router = useRouter()
  const [form, setForm] = useState<SignUpForm>({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    re_password: ""
  })
  const [err, setErr] = useState(false)
  const handleChange = (key: string, value: string) => {
    setErr(false)
    setForm((oldValue) => ({ ...oldValue, [key]: value }))
  }
  const handleSignUp = async () => {
    try {
      const { data, status } = await signUp(form)
      if (status === 201) {
        router.push("/sign-in")
      }
    } catch (error) {
      setErr(true)
      // Handle the error here
      console.error(error)
    }
  }
  return (
    <div className="max-w-full w-[560px] m-auto mt-[80px]">
      <div className="text-5xl font-medium mb-5 text-center">Sign Up</div>
      <div className="px-2 flex flex-col">
        <div className="mb-4">
          <div className="mb-2">First name</div>
          <input
            onChange={(e) => handleChange("first_name", e?.target?.value)}
            value={form.first_name}
            type="text"
            className="h-[36px] rounded px-2 border-[#5c5d6e] bg-[#343541] w-full"
          />
        </div>
        <div className="mb-4">
          <div className="mb-2">Last name</div>
          <input
            onChange={(e) => handleChange("last_name", e?.target?.value)}
            value={form.last_name}
            type="text"
            className="h-[36px] rounded px-2 border-[#5c5d6e] bg-[#343541] w-full"
          />
        </div>
        <div className="mb-4">
          <div className="mb-2">Email</div>
          <input
            onChange={(e) => handleChange("email", e?.target?.value)}
            value={form.email}
            type="email"
            className="h-[36px] rounded px-2 border-[#5c5d6e] bg-[#343541] w-full"
          />
        </div>
        <div className="mb-4">
          <div className="mb-2">Password</div>
          <input
            onChange={(e) => handleChange("password", e?.target?.value)}
            value={form.password}
            type="password"
            className="h-[36px] rounded px-2 border-[#5c5d6e] bg-[#343541] w-full"
          />
        </div>
        <div className="mb-4">
          <div className="mb-2">Re-password</div>
          <input
            onChange={(e) => handleChange("re_password", e?.target?.value)}
            value={form.re_password}
            type="password"
            className="h-[36px] rounded px-2 border-[#5c5d6e] bg-[#343541] w-full"
          />
        </div>
        <button
          className="mx-auto px-4 py-1 font-medium bg-gray-800 rounded-2xl hover:bg-gray-400"
          onClick={handleSignUp}
        >
          Sign Up
        </button>
        {err && (
          <div className="text-center text-red-400 text-sm mt-2">
            An error occurred. Please try again
          </div>
        )}
      </div>
    </div>
  )
}

export default SignUp
