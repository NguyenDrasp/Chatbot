import { signIn } from "@/api/SignIn"
import { useRouter } from "next/navigation"
import React, { useState } from "react"

type Props = {}

export type SignInForm = {
  email: ""
  password: ""
}

const SignIn = (props: Props) => {
  const router = useRouter()
  const [form, setForm] = useState<SignInForm>({
    email: "",
    password: ""
  })
  const [err, setErr] = useState(false)
  const handleChange = (key: string, value: string) => {
    setErr(false)
    setForm((oldValue) => ({ ...oldValue, [key]: value }))
  }
  const handleSignIn = async () => {
    try {
      const { data, status } = await signIn(form)
      if (status === 200) {
        localStorage.setItem("access_token", data.access)
        localStorage.setItem("refresh_token", data.refesh)
        router.push("/")
      }
    } catch (error) {
      setErr(true)
      // Handle the error here
      console.error(error)
    }
  }
  return (
    <div className="max-w-full w-[560px] m-auto mt-[80px]">
      <div className="text-5xl font-medium mb-5 text-center">Sign In</div>
      <div className="px-2 flex flex-col">
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
        <div className="flex relative">
          <button
            className="mx-auto px-4 py-1 font-medium bg-gray-800 rounded-2xl hover:bg-gray-400"
            onClick={handleSignIn}
          >
            Sign In
          </button>
          <div className="flex gap-2 items-center absolute right-0">
            Or
            <button
              className="mx-auto px-4 py-1 font-medium bg-gray-800 rounded-2xl hover:bg-gray-400"
              onClick={() => {
                router.push("/sign-up")
              }}
            >
              Sign Up
            </button>
          </div>
        </div>
        {err && (
          <div className="text-center text-red-400 text-sm mt-2">
            An error occurred. Please try again
          </div>
        )}
      </div>
    </div>
  )
}

export default SignIn
