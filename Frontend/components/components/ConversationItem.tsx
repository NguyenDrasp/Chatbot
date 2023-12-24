import { cn } from "@/lib/utils"
import React from "react"

type Props = { isQuestion?: boolean; content?: string, modalName?: string }

const ConversationItem = ({ isQuestion, content, modalName }: Props) => {
  const contentWithBreaks = content.replace(/\n/g, '<br />');
  console.log(modalName)
  if (!content) return null
  return (  
    <div className="flex gap-1 p-4 mx-2 flex-col md:px-4 md:last:pb-6 lg:mx-auto lg:max-w-2xl xl:max-w-3xl">
      <div className="flex gap-3">
        <div
          className={cn("rounded-full h-6 w-6", {
            "bg-gray-500": isQuestion,
            "bg-green-500": !isQuestion
          })}
        ></div>
        <div className="font-semibold ">{isQuestion ? "You" : modalName}</div>
      </div>
      <div className="flex-1">
        <span dangerouslySetInnerHTML={{__html: contentWithBreaks}}/>
      </div>
    </div>
  )
}

export default ConversationItem
