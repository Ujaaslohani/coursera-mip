import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";

// QUERY HOOK — CALLS GET /api/conversations/{conversationId}/messages
export const useConversationMessages = (conversationId: string | null) => {
  return useQuery({
    queryKey: ["conversation-messages", conversationId],
    queryFn: async () => {
      if (!conversationId) return [];
      const { data } = await api.get<any[]>(`/api/conversations/${conversationId}/messages`);
      return data;
    },
    enabled: !!conversationId,
    staleTime: 30_000,
  });
};
