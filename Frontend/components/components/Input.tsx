import React, { Dispatch, SetStateAction } from "react"
import { Textarea, TextareaProps } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

type Props = TextareaProps & {
  className?: string
  value?: string
  onInputChange?: (e: string) => void
  requestToServer?: (payload: any) => Promise<void>
}

const Input = ({
  className,
  value,
  onInputChange,
  requestToServer,
  ...props
}: Props) => {
  const handleOnChange: React.ChangeEventHandler<HTMLTextAreaElement> = (e) => {
    onInputChange?.(e?.target?.value)
  }
  const handleOnKeyUp: React.KeyboardEventHandler<HTMLTextAreaElement> = (
    e
  ) => {
    if (e?.keyCode === 13) {
      requestToServer?.({
        query: value
      })
      onInputChange?.("")
    }
  }

  return (
    <Textarea
      onChange={handleOnChange}
      onKeyUp={handleOnKeyUp}
      value={value}
      {...props}
      className={cn(
        "rounded-xl h-[52px] min-h-[52px] overflow-hidden resize-y border-[#5c5d6e] bg-[#343541] m-0 w-full pr-10 focus:ring-0 focus-visible:ring-0 md:py-4 md:pr-12 pl-3 md:pl-4",
        className
      )}
    />
  )
}

export default Input
