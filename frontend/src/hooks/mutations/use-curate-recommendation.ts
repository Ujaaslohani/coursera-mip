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
      const { data } = await api.post<CurateRecommendationResponse>(
        "/api/recommendations",
        payload
      );
      return data;
    },
  });
};
