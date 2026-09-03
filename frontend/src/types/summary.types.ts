// SUPABASE DASHBOARD SUMMARY API RESPONSE INTERFACES
export interface DashboardActivitySummary {
  total_conversations?: number;
  total_queries?: number;
  total_responses?: number;
  total_evidence_records?: number;
  total_recommendations?: number;
  total_feedback_records?: number;
}

export interface DashboardFeedbackSummary {
  total_feedback_records?: number;
  helpful_count?: number;
  not_helpful_count?: number;
  approved_count?: number;
  rejected_count?: number;
  average_rating?: number;
}

export interface DashboardSummaryResponse {
  activity_summary?: DashboardActivitySummary;
  feedback_summary?: DashboardFeedbackSummary;
  popular_topics?: Array<Record<string, any>>;
  evidence_usage?: Array<Record<string, any>>;
  lecture_usage?: Array<Record<string, any>>;
}
