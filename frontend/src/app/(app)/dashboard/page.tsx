"use client";

import React, { useState, useMemo } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { RecommendationStats } from "@/components/dashboard/recommendation-stats";
import { PipelineHealthCard } from "@/components/dashboard/pipeline-health";
import { RefreshCw } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import { useMetrics } from "@/hooks/query/use-metrics";
import { useDashboardSummary } from "@/hooks/query/use-dashboard-summary";
import { DashboardStats } from "@/types";


export default function DashboardPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);

  // CONSUME REAL METRICS API VIA TANSTACK QUERY
  const {
    data: metrics,
    isLoading: isMetricsLoading,
    isFetching: isMetricsFetching,
    refetch: refetchMetrics,
  } = useMetrics(6000);

  // CONSUME REAL DASHBOARD SUMMARY API (SUPABASE VIEWS)
  const {
    data: summary,
    isFetching: isSummaryFetching,
    refetch: refetchSummary,
  } = useDashboardSummary();

  const totalIndexed = metrics?.points_count ?? 0;
  const totalRecommendations =
    summary?.activity_summary?.total_recommendations ?? 0;
  const acceptedRecommendations =
    summary?.feedback_summary?.approved_count ?? 0;
  const rejectedRecommendations =
    summary?.feedback_summary?.rejected_count ?? 0;
  const pendingRecommendations = Math.max(
    0,
    totalRecommendations - (acceptedRecommendations + rejectedRecommendations)
  );

  const stats: DashboardStats = useMemo(() => {
    return {
      totalJobs: totalIndexed,
      failedJobs: 0,
      totalAssets: totalIndexed,
      totalAssetsIndexed: totalIndexed,
      pendingReview: pendingRecommendations,
      recommendationsAccepted: acceptedRecommendations,
      totalRecommendationsCurated: totalRecommendations,
    };
  }, [
    totalIndexed,
    totalRecommendations,
    acceptedRecommendations,
    pendingRecommendations,
  ]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([refetchMetrics(), refetchSummary()]);
    } finally {
      setIsRefreshing(false);
    }
  };

  const isSyncing = isRefreshing || isMetricsFetching || isSummaryFetching;

  return (
    <div className="space-y-6 pb-10">
      {/* PAGE HEADER WITH ACTIONS */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <PageHeader
          title="Dashboard"
          description="Real-time multimodal pipeline telemetry, curriculum intelligence, and asset processing monitor."
        />

        <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isSyncing}
            className="h-9 gap-1.5 px-3.5"
          >
            {isSyncing ? (
              <Spinner className="w-3.5 h-3.5" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5" />
            )}
            {isSyncing ? "Syncing..." : "Sync"}
          </Button>
        </div>
      </div>

      {/* CORE PIPELINE & ASSET KPIS */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Pipeline & Ingestion Key Metrics
          </h2>
        </div>
        <StatsCards stats={stats} />
      </section>

      {/* MULTIMODAL PIPELINE MODALITY DISTRIBUTION & HEALTH */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Multimodal Pipeline Health & Conversion
          </h2>
        </div>
        <PipelineHealthCard metrics={metrics} isLoading={isMetricsLoading} />
      </section>

      {/* RECOMMENDATIONS METRICS */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Curriculum Recommendations & Human Review
          </h2>
        </div>
        <RecommendationStats stats={stats} />
      </section>
    </div>
  );
}
