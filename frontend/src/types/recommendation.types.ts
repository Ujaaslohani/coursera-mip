// CURATION API TYPES (POST /api/recommendations)
export interface CurateRecommendationRequest {
  insight_id: string;
  title: string;
  category?: string;
  recommendation_text: string;
  priority?: number;
  metadata?: Record<string, any>;
}

export interface CurateRecommendationResponse {
  recommendation_id: string;
  insight_id: string;
  status: string;
  message: string;
}