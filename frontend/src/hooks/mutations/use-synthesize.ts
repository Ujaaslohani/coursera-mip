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
      const { data } = await api.post<SynthesizeResponse>(
        "/api/synthesize",
        payload
      );
      return data;
    },
  });
};