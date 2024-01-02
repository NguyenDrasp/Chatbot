import { Inter } from "next/font/google"
import Input from "@/components/components/Input"
import ConversationItem from "./../components/components/ConversationItem"
import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useGetListSession } from "@/api/getListSession"
import { saveHistory } from "@/api/saveHistory"
import { newSession } from "@/api/newSession"
import { useGetOldHistory } from "@/api/getOldSessionHistory"
import { useKeycloak } from "@react-keycloak/ssr";

const inter = Inter({ subsets: ["latin"] })

const modals = [
  { label: "Chat GPT 3.5", link: process.env.NEXT_PUBLIC_URL },
  { label: "Llama 2 7b(NLPHUST)", link: process.env.NEXT_PUBLIC_URL_3 },
  { label: "PhoGPT", link: process.env.NEXT_PUBLIC_URL_2 }
]


export default function Home() {
  const { keycloak } = useKeycloak()
  
  const [sessionId, setSessionId] = useState({
    sessionId: null,
    isInit: true
  })
  const { data: listSession } = useGetListSession(
    keycloak?.idTokenParsed?.sub,
    sessionId.sessionId
  )
  const [input, setInput] = useState("")
  const [answer, setAnswer] = useState("")
  const [conversations, setConversations] = useState<{
    0: {
      type: "human" | "ai"
      data: {
        content: string

        additional_kwargs: {}
        type: "human" | "ai"
        example: false
      }
    }[]
    1: {
      type: "human" | "ai"
      data: {
        content: string

        additional_kwargs: {}
        type: "human" | "ai"
        example: false
      }
    }[]
    2: {
      type: "human" | "ai"
      data: {
        content: string

        additional_kwargs: {}
        type: "human" | "ai"
        example: false
      }
    }[]
  }>({ 0: [], 1: [], 2: [] })

  const [modal, setModal] = useState(0)

  const messagesEndRef = useRef(null)

  const { data: sessionHistory } = useGetOldHistory(sessionId.sessionId)

  useEffect(() => {
    if (
      sessionId.isInit &&
      !!sessionHistory &&
      !!sessionHistory?.data &&
      !!sessionHistory?.data?.data
    ) {
      setConversations((prev) => ({
        ...prev,
        [modal]: JSON.parse(sessionHistory?.data?.data)
      }))
    }
  }, [sessionId, sessionHistory, modal])

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
            type: "ai",
            data: {
              content: answer,
              additional_kwargs: {},
              type: "ai",
              example: false
            },
            modalName: modals[modal].label
          },
          {
            type: "human",
            data: {
              content: payload.query,
              additional_kwargs: {},
              type: "human",
              example: false
            }
          }
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
        body: JSON.stringify({
          ...payload,
          history: JSON.stringify(conversations?.[modal]?.slice(-5))
        })
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

  const handleSaveHistory = () => {
    if (!sessionId.sessionId) return
    saveHistory({
      session_id: sessionId.sessionId,
      history: JSON.stringify([
        ...conversations?.[modal]?.slice(-5),
        !!answer && {
          type: "ai",
          data: {
            content: answer,
            additional_kwargs: {},
            type: "ai",
            example: false
          },
          modalName: modals[modal].label
        }
      ])
    })
  }

  const createNewSession = (userId: string) => async () => {
    try {
      if (userId) {
        const res = await newSession(userId)
        setSessionId({ sessionId: res?.data?.session_id, isInit: true })
      }
    } catch (err) {
      console.log(err)
    }
  }

  return (
    <main className="flex bg-[#343541]">
      <div className="h-screen no-scrollbar overflow-y-scroll pl-3 pt-10 w-[200px] flex flex-col gap-4">
        <button
          onClick={createNewSession(keycloak?.idTokenParsed?.sub)}
          className="px-3 py-2 mb-5 bg-gray-800 rounded-2xl hover:!bg-gray-400"
        >
          Create new session
        </button>
        <div></div>
        <button 
          className="px-3 py-3 mt-10 bg-gray-800 rounded-2xl hover:!bg-gray-400" 
          onClick={async () => await keycloak.logout({ redirectUri: "http://localhost:3000" })} 
        >
          Logout
        </button>
        {listSession?.data?.session_ids?.map((session, index) => (
          <button
            key={index}
            onClick={() => {
              setSessionId({ sessionId: session, isInit: true })
              setAnswer("")
            }}
            className={`px-3 py-1 bg-gray-800 rounded-2xl hover:!bg-gray-400 ${
              sessionId.sessionId === session && "!bg-gray-400"
            }`}
          >
            Session {session}
          </button>
        ))}
        {!!sessionId.sessionId && (
          <button
            onClick={handleSaveHistory}
            className="px-3 py-2 mt-10 bg-gray-800 rounded-2xl hover:!bg-gray-400"
          >
            Save session history
          </button>
        )}
      </div>
      {!!sessionId.sessionId && (
        <div
          className={`flex-1 no-scrollbar flex min-h-screen flex-col items-center justify-between px-24 pt-10 relative ${inter.className}`}
        >
          <button className="fixed top-5 px-3 py-1 bg-gray-800 rounded-2xl hover:bg-gray-400">
            <a href="http://localhost:5000/">Map</a>
          </button>
          <div className="flex-1 mb-[148px] w-full">
        
            {conversations?.[modal]?.map((conversation, index) => (
              <ConversationItem
                key={index}
                content={conversation?.data?.content}
                isQuestion={conversation?.type === "human"}
                modalName={modals[modal].label}
              />
            ))}
            {!!answer && (
              <ConversationItem
                content={answer}
                modalName={modals[modal].label}
              />
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="fixed bottom-0 left-[200px] right-0 pb-10 bg-[#343541]">
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
        </div>
      )}
    </main>
  )
}
