"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { SearchInput } from "@/components/ui/search-input";
import { useSynthesize } from "@/hooks/mutations/use-synthesize";
import { useConversations } from "@/hooks/query/use-conversations";
import { useQueryClient } from "@tanstack/react-query";
import { InsightMessageCard } from "@/components/chat/insight-message-card";
import { type ChatMessage } from "@/types/chat.types";
import {
  Clock,
  ExternalLink,
  FileText,
  History,
  Loader,
  MessageSquare,
  Plus,
  SendHorizonal,
  Sparkles,
} from "lucide-react";
import React, { useRef, useState, useEffect } from "react";

function formatTimeAgo(isoString?: string | null): string {
  if (!isoString) return "Recently";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return "Recently";
  }
}

const Chat = () => {
  const [open, setOpen] = useState(false);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [historySearch, setHistorySearch] = useState("");

  // CHAT STATE
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const queryClient = useQueryClient();

  // CONVERSATIONS QUERY
  const {
    data: serverConversations = [],
    isLoading: isHistoryLoading,
    isFetching: isHistoryFetching,
  } = useConversations(50);

  // SYNTHESIZE MUTATION
  const synthesize = useSynthesize();

  // AUTO-SCROLL TO BOTTOM ON NEW MESSAGES
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // HANDLE SEND MESSAGE
  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || synthesize.isPending) return;

    // ADD USER MESSAGE
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");

    // CALL SYNTHESIZE API
    synthesize.mutate(
      {
        query: trimmed,
        conversation_id: conversationId ?? undefined,
      },
      {
        onSuccess: (data) => {
          // STORE CONVERSATION ID FOR FOLLOW-UPS
          if (!conversationId) setConversationId(data.conversation_id);
          setActiveChatId(data.conversation_id);

          // REFETCH CONVERSATION LIST IN BACKGROUND
          queryClient.invalidateQueries({ queryKey: ["conversations"] });

          // ADD ASSISTANT RESPONSE
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: data.answer_text,
              confidence: data.confidence,
              citations: data.citations,
            },
          ]);
        },
        onError: () => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Something went wrong. Please try again.",
            },
          ]);
        },
      },
    );
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setActiveChatId(null);
    setOpen(false);
  };

  const handleSelectChat = (id: string) => {
    setActiveChatId(id);
    setConversationId(id);
    setMessages([]);
    setOpen(false);
  };

  // MAP SERVER CONVERSATIONS
  const historyList = serverConversations.map((c) => ({
    id: c.conversation_id,
    title: c.title || `Conversation ${c.conversation_id.slice(0, 8)}`,
    timestamp: formatTimeAgo(c.last_activity_at || c.started_at),
    preview: c.session_id
      ? `Session: ${c.session_id}`
      : "Course learning analytics query",
  }));

  const filteredHistory = historyList.filter(
    (item) =>
      item.title.toLowerCase().includes(historySearch.toLowerCase()) ||
      item.preview.toLowerCase().includes(historySearch.toLowerCase()),
  );

  const activeChat = historyList.find((h) => h.id === activeChatId);

  return (
    <section className="relative flex flex-col h-[calc(100vh-6rem)] md:h-[calc(100vh-6.5rem)]">
      {/* FLOATING HEADER CONTROLS (NEW CHAT + HISTORY) */}
      <div className="absolute top-0 right-0 z-20 flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewChat}
          className="flex items-center gap-1.5 rounded-full bg-card/80 backdrop-blur-md shadow-md border-border/80 hover:bg-card text-foreground text-xs px-3 py-1.5 transition-all"
        >
          <Plus className="h-3.5 w-3.5 text-primary" />
          <span>New Chat</span>
        </Button>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger
            render={
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-1.5 rounded-full bg-card/80 backdrop-blur-md shadow-md border-border/80 hover:bg-card text-foreground text-xs px-3 py-1.5 transition-all"
              />
            }
          >
            <History className="h-3.5 w-3.5 text-primary" />
            <span className="inline-flex items-center gap-1">
              History
              {isHistoryFetching ? (
                <Loader className="h-3 w-3 animate-spin inline" />
              ) : (
                <span>({serverConversations.length})</span>
              )}
            </span>
          </DialogTrigger>

          <DialogContent className="sm:max-w-md p-5 gap-4">
            <DialogHeader className="gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="h-5 w-5 text-primary" />
                  <DialogTitle className="text-lg">Chat History</DialogTitle>
                </div>
              </div>
            </DialogHeader>

            {/* SEARCH INPUT */}
            <SearchInput
              value={historySearch}
              onChange={(e) => setHistorySearch(e.target.value)}
              placeholder="Search past conversations..."
              showClear
              onClear={() => setHistorySearch("")}
              className="h-9 text-sm"
            />

            {/* HISTORY LIST */}
            <div className="max-h-80 overflow-y-auto space-y-2 pr-1 -mr-1">
              {isHistoryLoading ? (
                <div className="flex items-center justify-center py-10 gap-2 text-sm text-muted-foreground">
                  <Loader className="h-4 w-4 animate-spin text-primary" />
                  <span>Loading history...</span>
                </div>
              ) : filteredHistory.length === 0 ? (
                <div className="text-center py-8 text-sm text-muted-foreground">
                  No conversation history found
                </div>
              ) : (
                filteredHistory.map((item) => {
                  const isActive = item.id === activeChatId;
                  return (
                    <div
                      key={item.id}
                      onClick={() => handleSelectChat(item.id)}
                      className={`group flex items-start justify-between gap-3 p-3 rounded-lg cursor-pointer transition-all border text-left ${
                        isActive
                          ? "bg-primary/10 border-primary/40 text-foreground"
                          : "bg-muted/30 border-transparent hover:bg-muted/70 text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-start gap-2.5 min-w-0 flex-1">
                        <MessageSquare
                          className={`h-4 w-4 mt-0.5 shrink-0 ${
                            isActive ? "text-primary" : "text-muted-foreground"
                          }`}
                        />
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium truncate text-foreground">
                            {item.title}
                          </p>
                          <p className="text-xs text-muted-foreground truncate mt-0.5">
                            {item.preview}
                          </p>
                          <div className="flex items-center gap-1.5 mt-1.5 text-[11px] text-muted-foreground/80">
                            <Clock className="h-3 w-3" />
                            <span>{item.timestamp}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* SCROLLABLE CHAT MESSAGES CONTAINER */}
      <main className="flex-1 overflow-y-auto space-y-4 pt-10 pr-1.5 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground text-sm gap-2 max-w-md mx-auto">
            <MessageSquare className="h-8 w-8 text-muted-foreground/50 mb-1" />
            <p className="font-medium text-foreground text-base">
              {activeChat ? activeChat.title : "New Conversation"}
            </p>
            <p className="text-xs text-muted-foreground">
              Ask anything about course friction, student misconceptions, or
              pedagogical improvements based on course evidence.
            </p>
            <div className="flex flex-wrap gap-2 justify-center mt-3">
              {[
                "Why are students dropping off in lecture 2?",
                "What is the common misconception in backprop?",
                "Suggest improvements for the intro module",
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setInput(suggestion)}
                  className="text-xs bg-muted/60 hover:bg-muted text-foreground/80 hover:text-foreground px-3 py-1.5 rounded-full border border-border/50 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${
                msg.role === "user" ? "items-end" : "items-start"
              }`}
            >
              {msg.role === "user" ? (
                <div className="max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-2.5 text-sm bg-primary text-primary-foreground shadow-xs leading-relaxed">
                  {msg.content}
                </div>
              ) : (
                <div className="w-full max-w-[95%] md:max-w-[85%] rounded-2xl p-4 sm:p-5 text-sm bg-card border border-border/70 shadow-xs">
                  <InsightMessageCard
                    content={msg.content}
                    confidence={msg.confidence}
                    citations={msg.citations}
                  />
                </div>
              )}
            </div>
          ))
        )}

        {/* LOADING INDICATOR */}
        {synthesize.isPending && (
          <div className="flex items-start">
            <div className="flex items-center gap-2.5 text-xs text-muted-foreground bg-muted/40 border border-border/40 px-3.5 py-2.5 rounded-2xl">
              <Loader className="h-3.5 w-3.5 animate-spin text-primary" />
              <span>
                Analyzing multimodal course evidence & synthesizing insights...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* INPUT FORM FOOTER */}
      <footer className="pt-2">
        <form onSubmit={handleSend} className="relative flex items-center">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about course friction or student difficulties..."
            disabled={synthesize.isPending}
            className="pr-12 py-5 rounded-full border-border/80 bg-card shadow-xs focus-visible:ring-primary text-sm"
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || synthesize.isPending}
            className="absolute right-1.5 h-8 w-8 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-all cursor-pointer"
          >
            {synthesize.isPending ? (
              <Loader className="h-4 w-4 animate-spin" />
            ) : (
              <SendHorizonal className="h-4 w-4" />
            )}
          </Button>
        </form>
      </footer>
    </section>
  );
};

export default Chat;
