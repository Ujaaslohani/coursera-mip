"use client";

import React, { createContext, useContext } from "react";
import {
  useChatSession,
  type UseChatSessionReturn,
} from "@/hooks/use-chat-session";

const ChatContext = createContext<UseChatSessionReturn | null>(null);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within a <ChatProvider>");
  }
  return context;
}

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const chat = useChatSession();
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
}
