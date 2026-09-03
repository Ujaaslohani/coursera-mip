"use client";

import React, { useMemo } from "react";
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
import { MetricsResponse } from "@/types/metrics.types";
import {
  Activity,
  FileText,
  Presentation,
  Film,
  MessagesSquare,
  HelpCircle,
  Layers,
} from "lucide-react";
import { PieChart, Pie, Cell } from "recharts";

interface PipelineHealthProps {
  metrics?: MetricsResponse | null;
  isLoading?: boolean;
}

const MODALITY_CONFIG: Record<
  string,
  {
    label: string;
    subtext: string;
    icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
    color: string;
    badgeVariant: "default" | "secondary" | "outline" | "info" | "warning";
  }
> = {
  caption: {
    label: "Captions",
    subtext: "Spoken lecture transcript chunks",
    icon: FileText,
    color: "#3B82F6",
    badgeVariant: "info",
  },
  slide: {
    label: "Slides",
    subtext: "Instructional slide images & text",
    icon: Presentation,
    color: "#8B5CF6",
    badgeVariant: "secondary",
  },
  frame: {
    label: "Video Frames",
    subtext: "Caption-aligned video frames",
    icon: Film,
    color: "#06B6D4",
    badgeVariant: "default",
  },
  discussion: {
    label: "Discussions",
    subtext: "Forum confusion threads & Q&A",
    icon: MessagesSquare,
    color: "#F59E0B",
    badgeVariant: "warning",
  },
  quiz: {
    label: "Quizzes",
    subtext: "Formative assessments & questions",
    icon: HelpCircle,
    color: "#EC4899",
    badgeVariant: "outline",
  },
};

export function PipelineHealthCard({ metrics, isLoading }: PipelineHealthProps) {
  const contentTypeCounts = metrics?.content_type_counts || {};
  const total =
    metrics?.points_count ??
    Object.values(contentTypeCounts).reduce((acc, val) => acc + val, 0);

  // DYNAMICALLY MAP MODALITY BREAKDOWN FROM LIVE API RESPONSE
  const modalityItems = useMemo(() => {
    return Object.entries(contentTypeCounts).map(([key, count]) => {
      const config = MODALITY_CONFIG[key.toLowerCase()] || {
        label: key.charAt(0).toUpperCase() + key.slice(1),
        subtext: "Indexed multimodal content",
        icon: Layers,
        color: "#64748B",
        badgeVariant: "secondary" as const,
      };
      const pct = total > 0 ? ((count / total) * 100).toFixed(1) : "0.0";
      return {
        key,
        label: config.label,
        value: count,
        percent: Number(pct),
        percentText: `${pct}%`,
        subtext: config.subtext,
        icon: config.icon,
        color: config.color,
        badgeVariant: config.badgeVariant,
      };
    });
  }, [contentTypeCounts, total]);

  // DATA FOR SHADCN / RECHARTS DONUT
  const chartData = useMemo(() => {
    return modalityItems.map((item) => ({
      name: item.label,
      value: item.value,
      color: item.color,
    }));
  }, [modalityItems]);

  const chartConfig = useMemo(() => {
    const cfg: ChartConfig = {};
    modalityItems.forEach((item) => {
      cfg[item.key] = {
        label: item.label,
        color: item.color,
      };
    });
    return cfg;
  }, [modalityItems]);

  return (
    <Card className="border-border/80 shadow-xs">
      <CardHeader className="border-b border-border/40 pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-md bg-muted text-primary border border-border/50">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <CardTitle className="text-lg font-heading">
                Multimodal Pipeline Distribution
              </CardTitle>
              <CardDescription className="text-xs mt-0.5">
                Lifecycle telemetry and throughput flow across all multimodal ingestion modalities.
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
            <span>{total.toLocaleString()} Total Ingested</span>
          </div>
          <div className="h-3 w-full rounded-full overflow-hidden flex bg-muted border border-border/50">
            {modalityItems.map((item) => (
              <div
                key={item.key}
                style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                className="transition-all duration-500"
                title={`${item.label}: ${item.value.toLocaleString()} (${item.percentText})`}
              />
            ))}
          </div>
        </div>

        {/* METRICS GRID & CHART */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          {/* BREAKDOWN CARDS */}
          <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {modalityItems.map((item) => {
              const ItemIcon = item.icon;
              return (
                <div
                  key={item.key}
                  className="p-3.5 rounded-lg border border-border/50 bg-muted/30 hover:bg-muted/50 transition-colors space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
                      <ItemIcon className="w-3.5 h-3.5" style={{ color: item.color }} />
                      <span className="truncate">{item.label}</span>
                    </div>
                    <Badge variant={item.badgeVariant} className="text-[10px] px-1.5 py-0">
                      {item.percentText}
                    </Badge>
                  </div>

                  <div className="text-xl font-bold font-heading text-foreground">
                    {item.value.toLocaleString()}
                  </div>

                  <div className="space-y-1">
                    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${item.percent}%`, backgroundColor: item.color }}
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
              Modality Breakdown
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
                    paddingAngle={chartData.length > 1 ? 2 : 0}
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
                  {total.toLocaleString()}
                </span>
                <span className="text-[10px] text-muted-foreground">Indexed</span>
              </div>
            </div>

            {/* MINIMAL LEGEND */}
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1.5 mt-2 text-[11px] w-full max-w-xs">
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
