import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";
import { type ConversationResponse } from "@/types/chat.types";

export const useConversations = (limit = 50) => {
  return useQuery({
    queryKey: ["conversations", limit],
    queryFn: async () => {
      const { data } = await api.get<ConversationResponse[]>("/api/conversations", {
        params: { limit },
      });
      return data;
    },
    staleTime: 30_000,
  });
};
