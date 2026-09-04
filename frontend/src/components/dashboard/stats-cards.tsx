"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DashboardStats } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { Layers, AlertTriangle, Database, FileCheck } from "lucide-react";

interface StatsCardsProps {
  stats: DashboardStats;
  isLoading?: boolean;
}

export function StatsCards({ stats, isLoading = false }: StatsCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {Array.from({ length: 4 }).map((_, idx) => (
          <Card key={idx} className="border-border/80">
            <CardContent className="p-4 flex flex-col justify-between h-full">
              <div className="flex items-start justify-between gap-2 mb-2">
                <Skeleton className="h-3.5 w-20" />
                <Skeleton className="h-7 w-7 rounded-md" />
              </div>
              <div className="space-y-1.5 my-1">
                <Skeleton className="h-6 w-16" />
                <Skeleton className="h-3 w-28" />
              </div>
              <div className="mt-2 pt-2 border-t border-border/40 flex items-center justify-between">
                <Skeleton className="h-4 w-20 rounded-md" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  const total = stats.totalAssets || 0;
  const indexed = stats.totalAssetsIndexed || 0;
  const totalJobs = stats.totalJobs || 0;
  const failedJobs = stats.failedJobs || 0;

  const indexedPercentage =
    total > 0 ? Math.round((indexed / total) * 100) : 100;
  const errorRate =
    totalJobs > 0 ? ((failedJobs / totalJobs) * 100).toFixed(1) : "0.0";

  const kpis = [
    {
      title: "Total Jobs",
      value: totalJobs.toLocaleString(),
      description: "Across all pipelines",
      icon: Layers,
      iconColor: "text-blue-600 dark:text-blue-400",
      badge: totalJobs > 0 ? "100% completed" : "0",
      badgeVariant: "info" as const,
    },
    {
      title: "Failed Jobs",
      value: failedJobs.toLocaleString(),
      description:
        failedJobs === 0 ? "No processing errors" : "Requires intervention",
      icon: AlertTriangle,
      iconColor: failedJobs > 0 ? "text-destructive" : "text-muted-foreground",
      badge: `${errorRate}% error`,
      badgeVariant:
        failedJobs > 0 ? ("destructive" as const) : ("secondary" as const),
    },
    {
      title: "Total Assets",
      value: total.toLocaleString(),
      description: "In multimodal repository",
      icon: Database,
      iconColor: "text-purple-600 dark:text-purple-400",
      badge: "Live Qdrant",
      badgeVariant: "secondary" as const,
    },
    {
      title: "Assets Indexed",
      value: indexed.toLocaleString(),
      description: `${indexedPercentage}% searchable coverage`,
      icon: FileCheck,
      iconColor: "text-cyan-600 dark:text-cyan-400",
      badge: `${indexedPercentage}% indexed`,
      badgeVariant: "info" as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {kpis.map((kpi, idx) => {
        const Icon = kpi.icon;
        return (
          <Card
            key={idx}
            className="transition-all duration-200 hover:shadow-xs border-border/80"
          >
            <CardContent className="p-4 flex flex-col justify-between h-full">
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="text-xs font-medium text-muted-foreground line-clamp-1">
                  {kpi.title}
                </span>
                <div
                  className={`p-1.5 rounded-md bg-muted border border-border/50 ${kpi.iconColor} shrink-0`}
                >
                  <Icon className="w-4 h-4" />
                </div>
              </div>

              <div className="space-y-1 my-1">
                <div className="text-xl font-bold tracking-tight text-foreground font-heading">
                  {kpi.value}
                </div>
                <p className="text-[11px] text-muted-foreground line-clamp-1">
                  {kpi.description}
                </p>
              </div>

              <div className="mt-2 pt-2 border-t border-border/40 flex items-center justify-between">
                <Badge
                  variant={kpi.badgeVariant}
                  className="text-[10px] px-1.5 py-0 h-4.5"
                >
                  {kpi.badge}
                </Badge>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
