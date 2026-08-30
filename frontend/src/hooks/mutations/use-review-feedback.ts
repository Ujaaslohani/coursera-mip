import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/api/axios";
import toast from "react-hot-toast";

export interface ReviewFeedbackPayload {
  response_id: string;
  decision: "accepted" | "rejected";
  notes?: string;
}

export const useReviewFeedback = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: ReviewFeedbackPayload) => {
      const { data } = await api.post("/api/review-feedback", payload);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      const action = variables.decision === "accepted" ? "accepted" : "rejected";
      toast.success(`Recommendation ${action} successfully`);
    },
    onError: (err: any) => {
      const msg =
        err?.response?.data?.message || err?.message || "Failed to submit review feedback";
      toast.error(msg);
    },
  });
};
