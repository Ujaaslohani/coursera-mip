import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";

// QUERY HOOK — CALLS GET /api/recommendations
export const useRecommendations = (limit = 50) => {
  return useQuery<any[]>({
    queryKey: ["recommendations", limit],
    queryFn: async () => {
      const { data } = await api.get("/api/recommendations", {
        params: { limit },
      });
      return data;
    },
  });
};
