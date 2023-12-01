import { Inter } from "next/font/google"
import Input from "@/components/components/Input"
import ConversationItem from "./../components/components/ConversationItem"
import { useState, useRef } from "react"

const inter = Inter({ subsets: ["latin"] })

export default function Home() {
  const [input, setInput] = useState("")
  const [answer, setAnswer] = useState("")
  const [conversations, setConversations] = useState<
    {
      isQuestion: boolean
      content: string
    }[]
  >([])

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
      setConversations([
        ...conversations,
        { isQuestion: false, content: answer },
        { isQuestion: true, content: payload.query }
      ])
      setAnswer("")
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_URL}/stream_chat/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        }
      )
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
      console.log("Streaming completed.")
    } catch (error) {
      // Xử lý lỗi nếu có
      console.error("Error during streaming request:", error)
    }
  }

  return (
    <main
      className={`flex min-h-screen flex-col items-center justify-between px-24 pt-10 bg-[#343541] relative ${inter.className}`}
    >
      <div className="flex-1 mb-[96px] w-full">
        {conversations?.map((conversation, index) => (
          <ConversationItem
            key={index}
            content={conversation?.content}
            isQuestion={conversation?.isQuestion}
          />
        ))}
        {!!answer && <ConversationItem content={answer} />}
        <div ref={messagesEndRef} />
      </div>
      <div className="fixed bottom-0 left-0 right-0 pb-10 bg-[#343541] pt-1">
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
