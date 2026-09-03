import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";
import { DashboardSummaryResponse } from "@/types/summary.types";

// QUERY HOOK — FETCHES AGGREGATE DASHBOARD SUMMARY (SUPABASE POSTGRES VIEWS)
export const useDashboardSummary = () => {
  return useQuery<DashboardSummaryResponse>({
    queryKey: ["dashboard-summary"],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummaryResponse>("/api/dashboard/summary");
      return data;
    },
    staleTime: 30_000,
  });
};
