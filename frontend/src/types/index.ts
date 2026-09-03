import type { ComponentType } from "react";

// INTERFACE FOR THE NAVIGATIONS 
export interface NavItem {
  title: string;
  url: string;
  icon: ComponentType<{ className?: string }>;
  badge?: string;
}

// TYPE AND INTERFACE FOR PROCESSING TABLE
export type Processing = {
  mode: string;
  topic: string;
  owner: string;
  stage: string;
  assetId: string;
};

export interface Citation {
  id: string;
  type: "transcript" | "image" | "video" | "audio" | "document" | string;
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
  citations?: Citation[];
  note?: string;
}

//REMOVE AND REFACTOR WITH REAL ONES AFTER GETTING APIS--------------------
// INTERFACES FOR DASHBOARD
export interface DashboardStats {
  totalJobs: number;
  failedJobs: number;
  pendingReview: number;
  recommendationsAccepted: number;
  totalAssets: number;
  totalAssetsIndexed: number;
  totalRecommendationsCurated: number;
}

export interface PipelineHealth {
  totalUploadedAssets: number;
  indexed: number;
  review: number;
  failed: number;
  searchable?: number;
  rejected?: number;
}

export interface DashboardData {
  stats: DashboardStats;
  pipelineHealth: PipelineHealth;
}


export * from "./chat.types";
export * from "./asset.types";
export * from "./login.types";
export * from "./recommendation.types";
export * from "./metrics.types";
export * from "./summary.types";


