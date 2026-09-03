"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { type ChatMessage } from "@/types/chat.types";
import { useConversations } from "@/hooks/query/use-conversations";
import { useConversationMessages } from "@/hooks/query/use-conversation-messages";
import { useSynthesize } from "@/hooks/mutations/use-synthesize";
import {
  formatServerMessages,
  mapServerConversations,
} from "@/components/chat/chat-helpers";

export interface UseChatSessionReturn {
  // STATE
  messages: ChatMessage[];
  input: string;
  activeChatId: string | null;
  activeChatTitle?: string;
  isMessagesFetching: boolean;
  isSynthesizing: boolean;

  // ACTIONS
  setInput: (value: string) => void;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  handleNewChat: () => void;
  handleSelectChat: (id: string) => void;
  handleCurateStep: (msgIndex: number, stepText?: string) => void;
}

const SESSION_KEY = "chat_session";

function readSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as { activeChatId: string | null; conversationId: string | null; input: string }) : null;
  } catch {
    return null;
  }
}

function writeSession(data: { activeChatId: string | null; conversationId: string | null; input: string }) {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(data));
  } catch {
  }
}

export function useChatSession(): UseChatSessionReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const chatIdParam = searchParams.get("id");

  // SEED STATE FROM SESSIONSTORAGE SO IT SURVIVES NAVIGATION-TRIGGERED UNMOUNTS
  const [activeChatId, setActiveChatId] = useState<string | null>(() => chatIdParam ?? readSession()?.activeChatId ?? null);
  const [conversationId, setConversationId] = useState<string | null>(() => chatIdParam ?? readSession()?.conversationId ?? null);
  const [input, setInput] = useState(() => readSession()?.input ?? "");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const queryClient = useQueryClient();

  // SERVER QUERIES — useConversations IS KEPT ONLY FOR THE ACTIVE CHAT TITLE LOOKUP
  const { data: serverConversations = [] } = useConversations(50);

  const { data: serverMessages = [], isFetching: isMessagesFetching } =
    useConversationMessages(activeChatId);

  const synthesize = useSynthesize();

  // PERSIST SESSION TO SESSIONSTORAGE WHENEVER KEY STATE CHANGES
  useEffect(() => {
    writeSession({ activeChatId, conversationId, input });
  }, [activeChatId, conversationId, input]);

  // SYNC STATE IF URL QUERY PARAM CHANGES DIRECTLY
  useEffect(() => {
    if (chatIdParam !== activeChatId) {
      setActiveChatId(chatIdParam);
      setConversationId(chatIdParam);
    }
  }, [chatIdParam]);

  // SYNC SERVER MESSAGES TO LOCAL MESSAGES
  useEffect(() => {
    if (activeChatId && serverMessages.length > 0) {
      setMessages(formatServerMessages(serverMessages));
    } else if (activeChatId && serverMessages.length === 0 && !isMessagesFetching) {
      if (!messages.some((m) => m.insightId)) {
        // KEEP OPTIMISTIC MESSAGES
      } else {
        setMessages([]);
      }
    }
  }, [serverMessages, activeChatId, isMessagesFetching]);

  // ACTIVE CHAT METADATA
  const activeChat = useMemo(() => {
    if (!activeChatId) return null;
    const history = mapServerConversations(serverConversations);
    return history.find((h) => h.id === activeChatId) || null;
  }, [serverConversations, activeChatId]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setInput(e.target.value);
    },
    []
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const trimmed = input.trim();
      if (!trimmed || synthesize.isPending) return;

      console.log("[useChatSession] Submitting message:", {
        query: trimmed,
        conversationId,
      });

      // ADD USER MESSAGE OPTIMISTICALLY
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: trimmed,
        },
      ]);
      setInput("");

      synthesize.mutate(
        {
          query: trimmed,
          conversation_id: conversationId ?? undefined,
        },
        {
          onSuccess: (data) => {
            console.log("[useChatSession] Synthesis success:", data);
            if (!conversationId) setConversationId(data.conversation_id);
            setActiveChatId(data.conversation_id);

            if (activeChatId !== data.conversation_id) {
              router.push(`?id=${data.conversation_id}`);
            }

            queryClient.invalidateQueries({ queryKey: ["conversations"] });

            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: data.answer_text,
                confidence: data.confidence,
                citations: data.citations,
                insightId: data.insight_id,
                recommendedAction: data.recommended_action,
              },
            ]);
          },
          onError: (error) => {
            console.error("[useChatSession] Synthesis error:", error);
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: "Something went wrong. Please try again.",
              },
            ]);
          },
        }
      );
    },
    [input, synthesize, conversationId, activeChatId, router, queryClient]
  );

  const handleNewChat = useCallback(() => {
    console.log("[useChatSession] Starting new chat");
    setMessages([]);
    setConversationId(null);
    setActiveChatId(null);
    setInput("");
    // CLEAR PERSISTED SESSION SO A FRESH /CHAT LOADS BLANK
    try { sessionStorage.removeItem(SESSION_KEY); } catch { /* ignore */ }
    router.push("/chat");
  }, [router]);

  const handleSelectChat = useCallback(
    (id: string) => {
      console.log("[useChatSession] Selected chat:", id);
      setActiveChatId(id);
      setConversationId(id);
      setMessages([]);
      router.push(`?id=${id}`);
    },
    [router]
  );

  const handleCurateStep = useCallback(
    (msgIndex: number, stepText?: string) => {
      setMessages((prev) =>
        prev.map((m, i) => {
          if (i === msgIndex) {
            if (stepText) {
              return {
                ...m,
                isCurated: true,
                curatedSteps: [...(m.curatedSteps || []), stepText],
              };
            }
            return { ...m, isCurated: true };
          }
          return m;
        })
      );
    },
    []
  );

  return {
    messages,
    input,
    activeChatId,
    activeChatTitle: activeChat?.title,
    isMessagesFetching,
    isSynthesizing: synthesize.isPending,
    setInput,
    handleInputChange,
    handleSubmit,
    handleNewChat,
    handleSelectChat,
    handleCurateStep,
  };
}
