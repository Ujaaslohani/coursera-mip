import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Loader, SendHorizonal } from "lucide-react"
import React, { useRef } from "react"
import { cn } from "@/lib/utils"

export interface ChatBottombarProps {
  input: string
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  isLoading?: boolean
  className?: string
}

export const ChatBottombar = ({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  className,
}: ChatBottombarProps) => {
  const formRef = useRef<HTMLFormElement>(null)

  return (
    <div className={cn("p-2", className)}>
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        className="relative flex items-center w-full"
      >
        <Input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask a question about course friction or student difficulties..."
          disabled={isLoading}
          className="pr-12 py-5 rounded-full border-border/80 bg-card shadow-xs focus-visible:ring-primary text-sm w-full"
        />
        <Button
          type="submit"
          size="icon"
          disabled={!input.trim() || isLoading}
          className="absolute right-1.5 h-8 w-8 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-all cursor-pointer"
        >
          {isLoading ? (
            <Loader className="h-4 w-4 animate-spin" />
          ) : (
            <SendHorizonal className="h-4 w-4" />
          )}
        </Button>
      </form>
    </div>
  )
}
