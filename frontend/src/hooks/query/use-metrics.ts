import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";
import { MetricsResponse } from "@/types/metrics.types";

// QUERY HOOK — FETCHES QDRANT COLLECTION METRICS (LIVE DATABASE COUNTS)
export const useMetrics = (scanLimit = 6000) => {
  return useQuery({
    queryKey: ["metrics", scanLimit],
    queryFn: async () => {
      const { data } = await api.get<MetricsResponse>("/api/metrics", {
        params: { scan_limit: scanLimit },
      });
      return data;
    },
    staleTime: 30_000,
  });
};