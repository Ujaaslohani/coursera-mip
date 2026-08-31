"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import {
  dashboardStats,
  pipelineHealthData,
  processingMonitorData,
} from "@/temp-data/dashboard-data";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { RecommendationStats } from "@/components/dashboard/recommendation-stats";
import { PipelineHealthCard } from "@/components/dashboard/pipeline-health";
import { ProcessingMonitorTable } from "@/components/dashboard/processing-monitor";
import { RefreshCw } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";

export default function DashboardPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<string>("Just now");

  // TODO: IMPLEMENT REAL FETCH FROM BACKEND 
  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setLastRefreshed("Just now");
    }, 800);
  };

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
            disabled={isRefreshing}
            className="h-9 gap-1.5 px-3.5"
          >
            {isRefreshing ? (
              <Spinner className="w-3.5 h-3.5" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5" />
            )}
            {isRefreshing ? "Syncing..." : "Sync"}
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
        <StatsCards stats={dashboardStats} />
      </section>

      {/* PIPELINE HEALTH */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Multimodal Pipeline Health & Conversion
          </h2>
        </div>
        <PipelineHealthCard health={pipelineHealthData} />
      </section>

      {/* RECOMMENDATIONS METRICS (SEPARATE SECTION) */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Curriculum Recommendations & Human Review
          </h2>
        </div>
        <RecommendationStats stats={dashboardStats} />
      </section>

      {/* PROCESSING MONITOR DATA TABLE */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Processing & Segmentation Monitor
          </h2>
        </div>
        <ProcessingMonitorTable items={processingMonitorData} />
      </section>
    </div>
  );
}
