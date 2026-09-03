"use client";

import React from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { DashboardStats } from "@/types";
import {
  BadgeCheck,
  CheckCircle2,
  Clock,
  ArrowRight,
} from "lucide-react";

interface RecommendationStatsProps {
  stats: DashboardStats;
}

export function RecommendationStats({ stats }: RecommendationStatsProps) {
  const totalCurated = stats.totalRecommendationsCurated || 0;

  const acceptanceRate =
    totalCurated > 0
      ? Math.round((stats.recommendationsAccepted / totalCurated) * 100)
      : 0;
  const pendingPct =
    totalCurated > 0
      ? Math.round((stats.pendingReview / totalCurated) * 100)
      : 0;

  const recommendationMetrics = [
    {
      title: "Recommendations Curated",
      value: totalCurated.toLocaleString(),
      description: "AI-generated multimodal curriculum insights",
      icon: BadgeCheck,
      iconColor: "text-primary",
      badge: "Total Output",
      badgeVariant: "default" as const,
      detail: "Based on learner telemetry & quiz drop-offs",
    },
    {
      title: "Recommendations Accepted",
      value: stats.recommendationsAccepted.toLocaleString(),
      description: `${acceptanceRate}% adoption by course instructors`,
      icon: CheckCircle2,
      iconColor: "text-emerald-600 dark:text-emerald-400",
      badge: `${acceptanceRate}% Accepted`,
      badgeVariant: "success" as const,
      detail: "Applied to live curriculum content",
    },
    {
      title: "Pending to Review",
      value: stats.pendingReview.toLocaleString(),
      description: `${pendingPct}% in active human-in-the-loop queue`,
      icon: Clock,
      iconColor: "text-amber-600 dark:text-amber-400",
      badge: "Action Required",
      badgeVariant: "warning" as const,
      detail: "Awaiting educator review and decision",
    },
  ];

  return (
    <Card className="border-border/80 shadow-xs overflow-hidden">
      <CardHeader className="border-b border-border/40 pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-md bg-muted text-primary border border-border/50">
              <BadgeCheck className="w-5 h-5" />
            </div>
            <div>
              <CardTitle className="text-lg font-heading">
                Curriculum Recommendations
              </CardTitle>
              <CardDescription className="text-xs mt-0.5">
                Multimodal learning interventions and instructor approval metrics.
              </CardDescription>
            </div>
          </div>

          <Link
            href="/recommendations"
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "h-8 gap-1.5 text-xs self-start sm:self-auto"
            )}
          >
            <span>View All Recommendations</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </CardHeader>

      <CardContent className="p-5">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendationMetrics.map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <div
                key={idx}
                className="p-4 rounded-lg border border-border/50 bg-muted/30 hover:bg-muted/50 transition-colors flex flex-col justify-between"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-xs font-medium text-muted-foreground">
                    {metric.title}
                  </span>
                  <div
                    className={`p-1.5 rounded-md bg-muted border border-border/50 ${metric.iconColor} shrink-0`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                </div>

                <div className="space-y-1 my-1.5">
                  <div className="text-2xl font-bold font-heading text-foreground">
                    {metric.value}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {metric.description}
                  </p>
                </div>

                <div className="mt-3 pt-3 border-t border-border/40 flex items-center justify-between">
                  <span className="text-[11px] text-muted-foreground">
                    {metric.detail}
                  </span>
                  <Badge variant={metric.badgeVariant} className="text-[10px] px-1.5 py-0">
                    {metric.badge}
                  </Badge>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
