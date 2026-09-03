import {
  DashboardData,
  DashboardStats,
  PipelineHealth,
} from "@/types";

// 1, 2, 4. DASHBOARD KEY METRICS (BASELINE)
export const dashboardStats: DashboardStats = {
  totalJobs: 0,
  failedJobs: 0,
  pendingReview: 0,
  recommendationsAccepted: 0,
  totalAssets: 0,
  totalAssetsIndexed: 0,
  totalRecommendationsCurated: 0,
};

// 3. PIPELINE HEALTH METRICS (BASELINE)
export const pipelineHealthData: PipelineHealth = {
  totalUploadedAssets: 0,
  indexed: 0,
  review: 0,
  failed: 0,
};

// COMBINED DASHBOARD DATA OBJECT
export const dashboardData: DashboardData = {
  stats: dashboardStats,
  pipelineHealth: pipelineHealthData,
};

