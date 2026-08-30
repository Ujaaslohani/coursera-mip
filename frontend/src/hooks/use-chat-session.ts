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
  // State
  messages: ChatMessage[];
  input: string;
  activeChatId: string | null;
  activeChatTitle?: string;
  isMessagesFetching: boolean;
  isSynthesizing: boolean;
  serverConversations: any[];
  isHistoryLoading: boolean;
  isHistoryFetching: boolean;

  // Actions
  setInput: (value: string) => void;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  handleNewChat: () => void;
  handleSelectChat: (id: string) => void;
  handleCurateStep: (msgIndex: number, stepText?: string) => void;
}

export function useChatSession(): UseChatSessionReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const chatIdParam = searchParams.get("id");

  const [activeChatId, setActiveChatId] = useState<string | null>(chatIdParam);
  const [conversationId, setConversationId] = useState<string | null>(chatIdParam);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const queryClient = useQueryClient();

  // Server Queries
  const {
    data: serverConversations = [],
    isLoading: isHistoryLoading,
    isFetching: isHistoryFetching,
  } = useConversations(50);

  const { data: serverMessages = [], isFetching: isMessagesFetching } =
    useConversationMessages(activeChatId);

  const synthesize = useSynthesize();

  // Sync state if URL query param changes directly
  useEffect(() => {
    if (chatIdParam !== activeChatId) {
      setActiveChatId(chatIdParam);
      setConversationId(chatIdParam);
    }
  }, [chatIdParam]);

  // Sync server messages to local messages
  useEffect(() => {
    if (activeChatId && serverMessages.length > 0) {
      setMessages(formatServerMessages(serverMessages));
    } else if (activeChatId && serverMessages.length === 0 && !isMessagesFetching) {
      if (!messages.some((m) => m.insightId)) {
        // Keep optimistic messages
      } else {
        setMessages([]);
      }
    }
  }, [serverMessages, activeChatId, isMessagesFetching]);

  // Active chat metadata
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

      // Add user message optimistically
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
          onError: () => {
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
    setMessages([]);
    setConversationId(null);
    setActiveChatId(null);
    router.push("/chat");
  }, [router]);

  const handleSelectChat = useCallback(
    (id: string) => {
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
    serverConversations,
    isHistoryLoading,
    isHistoryFetching,
    setInput,
    handleInputChange,
    handleSubmit,
    handleNewChat,
    handleSelectChat,
    handleCurateStep,
  };
}
