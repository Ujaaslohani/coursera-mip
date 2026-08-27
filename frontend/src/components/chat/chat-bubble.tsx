import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const chatBubbleVariants = cva(
  "flex w-max max-w-[85%] md:max-w-[70%] flex-col gap-2 rounded-2xl px-4 py-2.5 text-sm",
  {
    variants: {
      variant: {
        sent: "bg-primary text-primary-foreground shadow-xs",
        received: "bg-card border border-border/70 shadow-xs text-foreground p-4 sm:p-5 w-full max-w-[95%] md:max-w-[85%]",
      },
      layout: {
        sent: "ml-auto",
        received: "mr-auto",
      },
    },
    defaultVariants: {
      variant: "sent",
      layout: "sent",
    },
  }
)

export interface ChatBubbleProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chatBubbleVariants> {}

const ChatBubble = React.forwardRef<HTMLDivElement, ChatBubbleProps>(
  ({ className, variant, layout, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(chatBubbleVariants({ variant, layout, className }))}
      {...props}
    />
  )
)
ChatBubble.displayName = "ChatBubble"

export { ChatBubble, chatBubbleVariants }
