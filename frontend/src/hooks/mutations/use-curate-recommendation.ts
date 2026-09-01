import { useMutation } from "@tanstack/react-query";
import api from "@/api/axios";
import {
  type CurateRecommendationRequest,
  type CurateRecommendationResponse,
} from "@/types/recommendation.types";

export type { CurateRecommendationRequest, CurateRecommendationResponse };

// MUTATION HOOK — CALLS POST /api/recommendations
export const useCurateRecommendation = () => {
  return useMutation({
    mutationFn: async (payload: CurateRecommendationRequest) => {
      console.log("[useCurateRecommendation] Curating recommendation:", payload);
      const { data } = await api.post<CurateRecommendationResponse>(
        "/api/recommendations",
        payload
      );
      return data;
    },
    onSuccess: (data) => {
      console.log("[useCurateRecommendation] Curated recommendation successfully:", data);
    },
    onError: (error) => {
      console.error("[useCurateRecommendation] Failed to curate recommendation:", error);
    },
  });
};
