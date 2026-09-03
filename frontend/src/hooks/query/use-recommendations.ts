import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";

interface UseRecommendationsParams {
  page: number;
  pageSize: number;
}

// QUERY HOOK — CALLS GET /api/recommendations WITH SERVER-SIDE PAGINATION
export const useRecommendations = ({ page, pageSize }: UseRecommendationsParams) => {
  const offset = page * pageSize;
  return useQuery<any[]>({
    queryKey: ["recommendations", page, pageSize],
    queryFn: async () => {
      const { data } = await api.get("/api/recommendations", {
        params: { limit: pageSize, offset },
      });
      return data;
    },
    staleTime: 30_000,
    placeholderData: (prev) => prev, // KEEP PREVIOUS PAGE DATA WHILE NEXT PAGE LOADS
  });
};
