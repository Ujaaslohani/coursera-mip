"use client";

import React, { useRef, useEffect } from "react";
import { ChatMessageList } from "@/components/chat/chat-message-list";
import { ChatBubble } from "@/components/chat/chat-bubble";
import { InsightMessageCard } from "@/components/chat/insight-message-card";
import { Spinner } from "@/components/ui/spinner";
import { ChatEmptyState } from "./chat-empty-state";
import { useChatContext } from "./chat-context";

export function ChatMessagesView() {
  const {
    messages,
    isMessagesFetching,
    isSynthesizing,
    activeChatTitle,
    setInput,
    handleCurateStep,
  } = useChatContext();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // AUTO-SCROLL TO BOTTOM ON NEW MESSAGES OR SYNTHESIS STATUS
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSynthesizing]);

  return (
    <main className="flex-1 overflow-y-auto space-y-4 pt-10 pr-1.5 custom-scrollbar">
      {isMessagesFetching && messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <Spinner className="h-6 w-6 text-muted-foreground" />
        </div>
      ) : messages.length === 0 ? (
        <ChatEmptyState
          title={activeChatTitle}
          onSelectSuggestion={setInput}
        />
      ) : (
        <ChatMessageList>
          {messages.map((msg, idx) => (
            <ChatBubble
              key={idx}
              variant={msg.role === "user" ? "sent" : "received"}
              layout={msg.role === "user" ? "sent" : "received"}
            >
              {msg.role === "user" ? (
                msg.content
              ) : (
                <InsightMessageCard
                  content={msg.content}
                  confidence={msg.confidence}
                  citations={msg.citations}
                  insightId={msg.insightId}
                  recommendedAction={msg.recommendedAction}
                  parsedInsight={msg.parsed}
                  isCurated={msg.isCurated}
                  curatedSteps={msg.curatedSteps}
                  onCurated={(stepText?: string) =>
                    handleCurateStep(idx, stepText)
                  }
                />
              )}
            </ChatBubble>
          ))}

          {/* SYNTHESIS LOADING INDICATOR */}
          {isSynthesizing && (
            <ChatBubble variant="received" layout="received">
              <div className="flex items-center gap-2.5 text-xs text-muted-foreground">
                <Spinner className="h-3.5 w-3.5 text-muted-foreground" />
                <span>
                  Analyzing multimodal course evidence & synthesizing insights...
                </span>
              </div>
            </ChatBubble>
          )}

          <div ref={messagesEndRef} />
        </ChatMessageList>
      )}
    </main>
  );
}
