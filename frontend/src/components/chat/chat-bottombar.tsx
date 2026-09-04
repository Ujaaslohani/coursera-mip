"use client";

import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SendHorizonal } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";
import { useChatContext } from "./chat-context";

export function ChatBottombar({ className }: { className?: string }) {
  const { input, handleInputChange, handleSubmit, isSynthesizing } =
    useChatContext();
  const formRef = useRef<HTMLFormElement>(null);

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
          disabled={isSynthesizing}
          className="pr-12 py-5 rounded-full border-border/80 bg-card shadow-xs focus-visible:ring-primary text-sm w-full"
        />
        <Button
          type="submit"
          size="icon"
          disabled={!input.trim() || isSynthesizing}
          className="absolute right-1.5 h-8 w-8 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-all cursor-pointer"
        >
          {isSynthesizing ? (
            <Spinner className="h-4 w-4 text-muted-foreground" />
          ) : (
            <SendHorizonal className="h-4 w-4" />
          )}
        </Button>
      </form>
    </div>
  );
}
