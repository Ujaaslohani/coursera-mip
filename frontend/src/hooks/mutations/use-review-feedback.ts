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
      console.log("[useReviewFeedback] Submitting feedback:", payload);
      const { data } = await api.post("/api/review-feedback", payload);
      return data;
    },
    onSuccess: (data, variables) => {
      console.log("[useReviewFeedback] Feedback submitted successfully:", {
        data,
        decision: variables.decision,
      });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      const action = variables.decision === "accepted" ? "accepted" : "rejected";
      toast.success(`Recommendation ${action} successfully`);
    },
    onError: (err: any) => {
      console.error("[useReviewFeedback] Error submitting review feedback:", err);
      const msg =
        err?.response?.data?.message || err?.message || "Failed to submit review feedback";
      toast.error(msg);
    },
  });
};
