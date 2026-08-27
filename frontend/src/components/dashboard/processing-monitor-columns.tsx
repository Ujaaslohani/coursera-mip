"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { type DataTableFeatures } from "@/constants/processing-table-features";
import { ProcessingMonitorItem } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Video,
  Image as ImageIcon,
  Captions,
  HelpCircle,
  MessagesSquare,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
} from "lucide-react";

const columnHelper =
  createColumnHelper<DataTableFeatures, ProcessingMonitorItem>();

export const getAssetTypeIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case "video":
      return <Video className="w-3.5 h-3.5 text-blue-500" />;
    case "image":
      return <ImageIcon className="w-3.5 h-3.5 text-emerald-500" />;
    case "transcript":
      return <Captions className="w-3.5 h-3.5 text-amber-500" />;
    case "quiz":
      return <HelpCircle className="w-3.5 h-3.5 text-cyan-500" />;
    case "discussion thread":
    case "discussion":
      return <MessagesSquare className="w-3.5 h-3.5 text-purple-500" />;
    default:
      return <Video className="w-3.5 h-3.5 text-muted-foreground" />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed":
      return (
        <Badge variant="success" className="gap-1 text-[11px] font-normal">
          <CheckCircle2 className="w-3 h-3" />
          Completed
        </Badge>
      );
    case "in_progress":
      return (
        <Badge variant="info" className="gap-1 text-[11px] font-normal">
          <Loader2 className="w-3 h-3 animate-spin" />
          Processing
        </Badge>
      );
    case "failed":
      return (
        <Badge variant="destructive" className="gap-1 text-[11px] font-normal">
          <XCircle className="w-3 h-3" />
          Failed
        </Badge>
      );
    case "review":
      return (
        <Badge variant="warning" className="gap-1 text-[11px] font-normal">
          <Clock className="w-3 h-3" />
          In Review
        </Badge>
      );
    case "queued":
      return (
        <Badge
          variant="outline"
          className="gap-1 text-[11px] font-normal text-muted-foreground"
        >
          <Clock className="w-3 h-3" />
          Queued
        </Badge>
      );
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
};

const getProgressColor = (status: string, progress: number) => {
  if (status === "failed") return "bg-rose-500";
  if (status === "review") return "bg-amber-500";
  if (progress === 100) return "bg-emerald-500";
  return "bg-primary";
};

export const processingMonitorColumns = columnHelper.columns([
  columnHelper.accessor("assetName", {
    header: "Asset Details",
    cell: (info) => {
      const item = info.row.original;
      return (
        <div className="space-y-0.5 max-w-sm">
          <div className="font-medium text-xs text-foreground line-clamp-1">
            {item.assetName}
          </div>
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground font-mono">
            <span className="text-primary font-semibold">{item.assetId}</span>
            {item.size && <span>• {item.size}</span>}
            {item.owner && <span>• {item.owner}</span>}
          </div>
        </div>
      );
    },
  }),
  columnHelper.accessor("assetType", {
    header: "Uploaded Type",
    cell: (info) => {
      const type = info.getValue();
      return (
        <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-muted border border-border/50 text-xs font-medium">
          {getAssetTypeIcon(type)}
          <span>{type}</span>
        </div>
      );
    },
  }),
  columnHelper.accessor("currentStage", {
    header: "Current Stage",
    cell: (info) => {
      const stage = info.getValue();
      const item = info.row.original;
      return (
        <div className="text-xs text-foreground font-medium flex items-center gap-1.5 max-w-[260px]">
          {item.status === "in_progress" && (
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0" />
          )}
          <span className="truncate">{stage}</span>
        </div>
      );
    },
  }),
  columnHelper.accessor("progress", {
    header: "Progress",
    cell: (info) => {
      const progress = info.getValue();
      const item = info.row.original;
      return (
        <div className="space-y-1.5 pr-2 min-w-[140px]">
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-mono font-medium text-foreground">
              {progress}%
            </span>
            <span className="text-[10px] text-muted-foreground">
              {progress === 100
                ? "Done"
                : item.status === "failed"
                ? "Halted"
                : "Processing"}
            </span>
          </div>
          <Progress
            value={progress}
            indicatorClassName={getProgressColor(item.status, progress)}
            className="h-1.5"
          />
        </div>
      );
    },
  }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: (info) => (
      <div className="text-right sm:text-left">
        {getStatusBadge(info.getValue())}
      </div>
    ),
  }),
]);
