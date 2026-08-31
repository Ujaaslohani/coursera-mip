"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SendHorizonal } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import React, { useRef } from "react";
import { cn } from "@/lib/utils";
import { useChatContext } from "./chat-context";

export interface ChatBottombarProps {
  input?: string;
  handleInputChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit?: (e: React.FormEvent<HTMLFormElement>) => void;
  isLoading?: boolean;
  className?: string;
}

export const ChatBottombar = ({
  input: propInput,
  handleInputChange: propHandleInputChange,
  handleSubmit: propHandleSubmit,
  isLoading: propIsLoading,
  className,
}: ChatBottombarProps = {}) => {
  const context = useChatContext();
  const formRef = useRef<HTMLFormElement>(null);

  const input = propInput !== undefined ? propInput : context.input;
  const handleInputChange = propHandleInputChange || context.handleInputChange;
  const handleSubmit = propHandleSubmit || context.handleSubmit;
  const isLoading = propIsLoading !== undefined ? propIsLoading : context.isSynthesizing;

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
            <Spinner className="h-4 w-4 text-muted-foreground" />
          ) : (
            <SendHorizonal className="h-4 w-4" />
          )}
        </Button>
      </form>
    </div>
  );
};
