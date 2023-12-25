import { Inter } from "next/font/google"
import Input from "@/components/components/Input"
import ConversationItem from "./../components/components/ConversationItem"
import { useState, useRef } from "react"
import { useCheckAuth } from "@/api/checkAuth"
import { useRouter } from "next/navigation"

const inter = Inter({ subsets: ["latin"] })

const modals = [
  { label: "Chat GPT 3.5", link: process.env.NEXT_PUBLIC_URL },
  { label: "Liama 2", link: process.env.NEXT_PUBLIC_URL_2 },
  { label: "PhoGPT 3", link: process.env.NEXT_PUBLIC_URL_2 }
]

export default function Home() {
  const router = useRouter()
  const { data, isLoading, status } = useCheckAuth()
  const [input, setInput] = useState("")
  const [answer, setAnswer] = useState("")
  const [conversations, setConversations] = useState<{
    0: {
      isQuestion: boolean
      content: string
    }[]
    1: {
      isQuestion: boolean
      content: string
    }[]
    2: {
      isQuestion: boolean
      content: string
    }[]
  }>({ 0: [], 1: [], 2: [] })

  const [modal, setModal] = useState(0)

  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    if (messagesEndRef) {
      messagesEndRef?.current?.scrollIntoView({ behavior: "smooth" })
    }
  }
  const handleInputChange = (e: string) => {
    setInput(e)
  }

  const requestToServer = async (payload: any) => {
    try {
      setConversations((prev) => ({
        ...prev,
        [modal]: [
          ...prev[modal],
          {
            isQuestion: false,
            content: answer,
            modalName: modals[modal].label
          },
          { isQuestion: true, content: payload.query }
        ]
      }))
      setAnswer("")
      const accessToken = localStorage.getItem("access_token")
      const response = await fetch(`${modals[modal].link}/stream_chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify(payload)
      })
      const reader = response?.body?.getReader()

      while (true) {
        const { done, value } = await reader?.read()
        const decoder = new TextDecoder()
        setAnswer((ans) => [ans, decoder.decode(value)].join(""))
        scrollToBottom()
        if (done) {
          break
        }
      }
      // Xử lý khi streaming kết thúc
    } catch (error) {
      // Xử lý lỗi nếu có
      console.error("Error during streaming request:", error)
    }
  }

  const applyModal = (newModal: number) => () => {
    setConversations({ 0: [], 1: [], 2: [] })
    setAnswer("")
    setModal(newModal)
  }

  if (!isLoading && status === 401) {
    router.push("/sign-in")
  }

  return (
    <main
      className={`flex min-h-screen flex-col items-center justify-between px-24 pt-10 bg-[#343541] relative ${inter.className}`}
    >
      <button className="fixed top-5 px-3 py-1 bg-gray-800 rounded-2xl hover:bg-gray-400">
        <a href="http://localhost:5000/">Map</a>
      </button>
      <div className="flex-1 mb-[148px] w-full">
        {conversations?.[modal]?.map((conversation, index) => (
          <ConversationItem
            key={index}
            content={conversation?.content}
            isQuestion={conversation?.isQuestion}
            modalName={modals[modal].label}
          />
        ))}
        {!!answer && (
          <ConversationItem content={answer} modalName={modals[modal].label} />
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="fixed bottom-0 left-0 right-0 pb-10 bg-[#343541]">
        <div className="stretch flex-row md:last:pb-6 lg:mx-auto lg:max-w-2xl xl:max-w-3xl flex gap-4 mb-2 items-center border-t pt-2">
          Select modal:
          {modals.map((mod, index) => (
            <button
              key={index}
              onClick={applyModal(index)}
              className={`px-3 py-1 bg-gray-800 rounded-2xl ${
                index === modal && "!bg-gray-400"
              }`}
            >
              {mod.label}
            </button>
          ))}
        </div>
        <Input
          value={input}
          requestToServer={requestToServer}
          onInputChange={handleInputChange}
          placeholder="Type your message here."
          className="stretch mx-2 flex flex-row gap-3 md:px-4 md:last:pb-6 lg:mx-auto lg:max-w-2xl xl:max-w-3xl"
        />
      </div>
    </main>
  )
}
