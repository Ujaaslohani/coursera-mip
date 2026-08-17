"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DashboardStats } from "@/types";
import {
  Layers,
  AlertTriangle,
  Database,
  FileCheck,
} from "lucide-react";

interface StatsCardsProps {
  stats: DashboardStats;
}

export function StatsCards({ stats }: StatsCardsProps) {
  const indexedPercentage = Math.round(
    (stats.totalAssetsIndexed / stats.totalAssets) * 100
  );

  const kpis = [
    {
      title: "Total Jobs",
      value: stats.totalJobs.toLocaleString(),
      description: "Across all pipelines",
      icon: Layers,
      iconColor: "text-blue-600 dark:text-blue-400",
      badge: "+12.4%",
      badgeVariant: "info" as const,
    },
    {
      title: "Failed Jobs",
      value: stats.failedJobs.toLocaleString(),
      description: "Requires intervention",
      icon: AlertTriangle,
      iconColor: "text-destructive",
      badge: `${((stats.failedJobs / stats.totalJobs) * 100).toFixed(1)}% error`,
      badgeVariant: "destructive" as const,
    },
    {
      title: "Total Assets",
      value: stats.totalAssets.toLocaleString(),
      description: "In multimodal repository",
      icon: Database,
      iconColor: "text-purple-600 dark:text-purple-400",
      badge: "+84 today",
      badgeVariant: "secondary" as const,
    },
    {
      title: "Assets Indexed",
      value: stats.totalAssetsIndexed.toLocaleString(),
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
                <Badge variant={kpi.badgeVariant} className="text-[10px] px-1.5 py-0 h-4.5">
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
