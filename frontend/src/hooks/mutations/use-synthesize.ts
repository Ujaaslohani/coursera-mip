import { useMutation } from "@tanstack/react-query";
import api from "@/api/axios";
import {
  type Citation,
  type SynthesizeRequest,
  type SynthesizeResponse,
} from "@/types/chat.types";

export type { Citation, SynthesizeRequest, SynthesizeResponse };

// MUTATION HOOK — CALLS POST /api/synthesize
export const useSynthesize = () => {
  return useMutation({
    mutationFn: async (payload: SynthesizeRequest) => {
      console.log("[useSynthesize] Calling /api/synthesize:", payload);
      const { data } = await api.post<SynthesizeResponse>(
        "/api/synthesize",
        payload
      );
      return data;
    },
    onSuccess: (data) => {
      console.log("[useSynthesize] Synthesize response received:", {
        insight_id: data.insight_id,
        conversation_id: data.conversation_id,
        confidence: data.confidence,
        citationsCount: data.citations?.length,
      });
    },
    onError: (error) => {
      console.error("[useSynthesize] Synthesize request failed:", error);
    },
  });
};