"use client";

import React, { Suspense } from "react";
import { ChatProvider } from "@/components/chat/chat-context";
import { ChatHeaderActions } from "@/components/chat/chat-header-actions";
import { ChatMessagesView } from "@/components/chat/chat-messages-view";
import { ChatBottombar } from "@/components/chat/chat-bottombar";
import { Spinner } from "@/components/ui/spinner";

function ChatLayout() {
  return (
    <section className="relative flex flex-col h-[calc(100vh-6rem)] md:h-[calc(100vh-6.5rem)]">
      {/* FLOATING HEADER CONTROLS (NEW CHAT + HISTORY DIALOG) */}
      <ChatHeaderActions />

      {/* SCROLLABLE CHAT MESSAGES FEED */}
      <ChatMessagesView />

      {/* INPUT FORM FOOTER */}
      <ChatBottombar />
    </section>
  );
}

export default function Chat() {
  return (
    <Suspense
      fallback={
        <div className="p-8 flex justify-center">
          <Spinner className="h-6 w-6 text-muted-foreground" />
        </div>
      }
    >
      <ChatProvider>
        <ChatLayout />
      </ChatProvider>
    </Suspense>
  );
}
