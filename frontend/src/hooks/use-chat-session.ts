"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { type ChatMessage } from "@/types/chat.types";
import { useConversationMessages } from "@/hooks/query/use-conversation-messages";
import { useSynthesize } from "@/hooks/mutations/use-synthesize";
import { formatServerMessages } from "@/components/chat/chat-helpers";
import { cleanCitationText } from "@/lib/citation-sanitizer";

const STORAGE_KEY = "mip_active_chat_id";

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

const EMPTY_SERVER_MESSAGES: any[] = [];

export function useChatSession(): UseChatSessionReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeChatId = searchParams.get("id");
  const hasRestoredRef = useRef(false);

  // RESTORE LAST ACTIVE CHAT WHEN NAVIGATING BACK TO /chat WITHOUT ?id=
  useEffect(() => {
    if (hasRestoredRef.current) return;
    if (!activeChatId) {
      try {
        const savedId = sessionStorage.getItem(STORAGE_KEY);
        if (savedId) {
          hasRestoredRef.current = true;
          router.replace(`/chat?id=${savedId}`);
          return;
        }
      } catch {
  
      }
    }
    hasRestoredRef.current = true;
  }, [activeChatId, router]);

  // PERSIST ACTIVE CHAT ID TO SESSION STORAGE
  useEffect(() => {
    if (activeChatId) {
      try {
        sessionStorage.setItem(STORAGE_KEY, activeChatId);
      } catch {
        // ignore
      }
    }
  }, [activeChatId]);

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const queryClient = useQueryClient();

  const { data: serverMessages = EMPTY_SERVER_MESSAGES, isFetching: isMessagesFetching } =
    useConversationMessages(activeChatId);

  const synthesize = useSynthesize();

  // SYNC SERVER MESSAGES TO LOCAL MESSAGES
  useEffect(() => {
    if (activeChatId && serverMessages.length > 0) {
      setMessages(formatServerMessages(serverMessages));
    } else if (!activeChatId) {
      setMessages((prev) => (prev.length > 0 ? [] : prev));
    }
  }, [serverMessages, activeChatId]);

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
          conversation_id: activeChatId ?? undefined,
        },
        {
          onSuccess: (data) => {
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
                citations: (data.citations || []).map((c) => ({
                  ...c,
                  text_preview: cleanCitationText(c.text_preview),
                })),
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
    [input, synthesize, activeChatId, router, queryClient]
  );

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setInput("");
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
    router.push("/chat");
  }, [router]);

  const handleSelectChat = useCallback(
    (id: string) => {
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
    activeChatTitle: undefined,
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
