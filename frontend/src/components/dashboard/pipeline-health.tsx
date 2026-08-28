"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { PipelineHealth } from "@/types";
import {
  Activity,
  CheckCircle2,
  Clock,
  XCircle,
  ShieldCheck,
} from "lucide-react";
import { PieChart, Pie, Cell } from "recharts";

interface PipelineHealthProps {
  health: PipelineHealth;
}

const PRIMARY_COLOR = "#4F6BFE";

const chartConfig = {
  indexed: {
    label: "Indexed",
    color: PRIMARY_COLOR,
  },
  review: {
    label: "In Review",
    color: "#F59E0B",
  },
  failed: {
    label: "Failed",
    color: "#EF4444",
  },
} satisfies ChartConfig;

export function PipelineHealthCard({ health }: PipelineHealthProps) {
  const total = health.totalUploadedAssets;
  const indexedPct = ((health.indexed / total) * 100).toFixed(1);
  const reviewPct = ((health.review / total) * 100).toFixed(1);
  const failedPct = ((health.failed / total) * 100).toFixed(1);

  // DATA FOR CHART USING PRIMARY APP COLOR FOR INDEXED
  const chartData = [
    { name: "Indexed", value: health.indexed, color: PRIMARY_COLOR },
    { name: "In Review", value: health.review, color: "#F59E0B" },
    { name: "Failed", value: health.failed, color: "#EF4444" },
  ];

  const breakdownItems = [
    {
      label: "Total Uploaded",
      value: health.totalUploadedAssets.toLocaleString(),
      subtext: "100% of pipeline input",
      icon: Activity,
      color: "text-foreground",
      badgeVariant: "secondary" as const,
      badgeText: "Base",
      barColor: "bg-muted-foreground/60",
      percent: 100,
    },
    {
      label: "Indexed",
      value: health.indexed.toLocaleString(),
      subtext: `${indexedPct}% processed & available`,
      icon: CheckCircle2,
      color: "text-primary",
      badgeVariant: "default" as const,
      badgeText: `${indexedPct}%`,
      barColor: "bg-primary",
      percent: Number(indexedPct),
    },
    {
      label: "In Review",
      value: health.review.toLocaleString(),
      subtext: `${reviewPct}% flagged for inspection`,
      icon: Clock,
      color: "text-amber-600 dark:text-amber-400",
      badgeVariant: "warning" as const,
      badgeText: `${reviewPct}%`,
      barColor: "bg-amber-500",
      percent: Number(reviewPct),
    },
    {
      label: "Failed",
      value: health.failed.toLocaleString(),
      subtext: `${failedPct}% processing errors`,
      icon: XCircle,
      color: "text-destructive",
      badgeVariant: "destructive" as const,
      badgeText: `${failedPct}%`,
      barColor: "bg-rose-500",
      percent: Number(failedPct),
    },
  ];

  return (
    <Card className="border-border/80 shadow-xs">
      <CardHeader className="border-b border-border/40 pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-md bg-muted text-primary border border-border/50">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <CardTitle className="text-lg font-heading">Pipeline Health</CardTitle>
              <CardDescription className="text-xs mt-0.5">
                Lifecycle telemetry and throughput flow across all multimodal ingestion pipelines.
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-5 space-y-6">
        {/* MULTI-STAGE FLOW VISUAL BAR */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-muted-foreground font-medium">
            <span>Pipeline Throughput Distribution</span>
            <span>{health.totalUploadedAssets.toLocaleString()} Total Ingested</span>
          </div>
          <div className="h-3 w-full rounded-full overflow-hidden flex bg-muted border border-border/50">
            <div
              style={{ width: `${indexedPct}%` }}
              className="bg-primary transition-all duration-500"
              title={`Indexed: ${health.indexed} (${indexedPct}%)`}
            />
            <div
              style={{ width: `${reviewPct}%` }}
              className="bg-amber-500 transition-all duration-500"
              title={`In Review: ${health.review} (${reviewPct}%)`}
            />
            <div
              style={{ width: `${failedPct}%` }}
              className="bg-rose-500 transition-all duration-500"
              title={`Failed: ${health.failed} (${failedPct}%)`}
            />
          </div>
        </div>

        {/* METRICS GRID & CHART */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          {/* BREAKDOWN CARDS */}
          <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {breakdownItems.map((item, index) => {
              const ItemIcon = item.icon;
              return (
                <div
                  key={index}
                  className="p-3.5 rounded-lg border border-border/50 bg-muted/30 hover:bg-muted/50 transition-colors space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
                      <ItemIcon className={`w-3.5 h-3.5 ${item.color}`} />
                      <span className="truncate">{item.label}</span>
                    </div>
                    <Badge variant={item.badgeVariant} className="text-[10px] px-1.5 py-0">
                      {item.badgeText}
                    </Badge>
                  </div>

                  <div className="text-xl font-bold font-heading text-foreground">
                    {item.value}
                  </div>

                  <div className="space-y-1">
                    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                      <div
                        className={`h-full ${item.barColor} rounded-full transition-all duration-500`}
                        style={{ width: `${item.percent}%` }}
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-1">
                      {item.subtext}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* SHADCN CHART CONTAINER & DONUT */}
          <div className="lg:col-span-4 p-4 rounded-xl border border-border/50 bg-muted/20 flex flex-col items-center justify-center">
            <div className="text-xs font-semibold text-foreground mb-1 text-center">
              Status Breakdown
            </div>
            <div className="relative w-full flex items-center justify-center">
              <ChartContainer
                config={chartConfig}
                className="w-full max-h-[170px] aspect-square"
              >
                <PieChart>
                  <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel nameKey="name" />}
                  />
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={46}
                    outerRadius={68}
                    paddingAngle={3}
                    strokeWidth={2}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="var(--card)" />
                    ))}
                  </Pie>
                </PieChart>
              </ChartContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-lg font-bold font-heading text-foreground">
                  {indexedPct}%
                </span>
                <span className="text-[10px] text-muted-foreground">Indexed</span>
              </div>
            </div>

            {/* MINIMAL LEGEND */}
            <div className="flex items-center justify-center gap-4 mt-2 text-[11px] w-full max-w-xs">
              {chartData.map((item, idx) => (
                <div key={idx} className="flex items-center gap-1.5">
                  <div
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-muted-foreground truncate">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
