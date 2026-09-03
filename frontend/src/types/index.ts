import type { ComponentType } from "react";

// INTERFACE FOR THE NAVIGATIONS 
export interface NavItem {
  title: string;
  url: string;
  icon: ComponentType<{ className?: string }>;
  badge?: string;
}

// INTERFACE FOR RECOMMENDATION CITATIONS
export interface RecommendationCitation {
  id: string;
  type: string;
  quote: string;
  explanation: string;
}

// INTERFACE FOR RECOMMENDATIONS
export interface Recommendation {
  id: string;
  title: string;
  queryBy: string;
  category: string;
  description?: string;
  timestamp: string;
  status?: "pending" | "curated" | "applied" | "rejected";
  suggestedAction?: string;
  citations?: RecommendationCitation[];
  note?: string;
}

// INTERFACES FOR DASHBOARD METRICS
export interface DashboardStats {
  totalJobs: number;
  failedJobs: number;
  pendingReview: number;
  recommendationsAccepted: number;
  totalAssets: number;
  totalAssetsIndexed: number;
  totalRecommendationsCurated: number;
}

// RE-EXPORT DOMAIN TYPES
export * from "./chat.types";
export * from "./login.types";
export * from "./recommendation.types";
export * from "./metrics.types";
export * from "./summary.types";
