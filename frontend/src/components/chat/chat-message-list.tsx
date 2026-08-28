import * as React from "react"
import { cn } from "@/lib/utils"

export interface ChatMessageListProps
  extends React.HTMLAttributes<HTMLDivElement> {}

const ChatMessageList = React.forwardRef<HTMLDivElement, ChatMessageListProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col w-full h-full p-4 gap-4", className)}
      {...props}
    >
      {children}
    </div>
  )
)
ChatMessageList.displayName = "ChatMessageList"

export { ChatMessageList }
