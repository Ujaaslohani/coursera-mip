"use client";

import React, { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ProcessingMonitorItem } from "@/types";
import { useTable } from "@tanstack/react-table";
import { features } from "@/constants/processing-table-features";
import { processingMonitorColumns } from "./processing-monitor-columns";

interface ProcessingMonitorProps {
  items: ProcessingMonitorItem[];
}

const columnWidths: Record<string, string> = {
  assetName: "w-[36%] min-w-[220px]",
  assetType: "w-[16%] min-w-[130px]",
  currentStage: "w-[24%] min-w-[180px]",
  progress: "w-[14%] min-w-[130px]",
  status: "w-[10%] min-w-[110px]",
};

// MODALITIES DEFINED IN REGISTER PAGE
const registerModalities = [
  { label: "All Types", value: "all" },
  { label: "Video", value: "video" },
  { label: "Image", value: "image" },
  { label: "Transcript", value: "transcript" },
  { label: "Quiz", value: "quiz" },
  { label: "Discussion Thread", value: "discussion" },
];

const statusOptions = [
  { label: "All Statuses", value: "all" },
  { label: "In Progress", value: "in_progress" },
  { label: "Completed", value: "completed" },
  { label: "In Review", value: "review" },
  { label: "Failed", value: "failed" },
  { label: "Queued", value: "queued" },
];

export function ProcessingMonitorTable({ items }: ProcessingMonitorProps) {
  const [globalFilter, setGlobalFilter] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  // PRE-FILTER DATA BASED ON TYPE & STATUS FILTERS BEFORE PASSING TO TANSTACK TABLE
  const filteredData = useMemo(() => {
    return items.filter((item) => {
      const itemType = item.assetType.toLowerCase();
      const matchesType =
        selectedType === "all" ||
        itemType === selectedType.toLowerCase() ||
        (selectedType === "discussion" && itemType.includes("discussion"));

      const matchesStatus =
        selectedStatus === "all" || item.status === selectedStatus;

      return matchesType && matchesStatus;
    });
  }, [items, selectedType, selectedStatus]);

  const table = useTable({
    features,
    data: filteredData,
    columns: processingMonitorColumns,
    state: {
      globalFilter,
    },
    onGlobalFilterChange: setGlobalFilter,
  });

  return (
    <Card className="border-border/80 shadow-xs overflow-hidden">
      <CardHeader className="border-b border-border/40 pb-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg font-heading">Processing Monitor</CardTitle>
              <Badge variant="secondary" className="font-mono text-xs">
                {filteredData.length} items
              </Badge>
            </div>
            <CardDescription className="text-xs mt-0.5">
              Live data table tracking multimodal asset ingestion, segmentation, and vector indexing progress.
            </CardDescription>
          </div>
        </div>

        {/* SEARCH AND FILTERS */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 pt-3">
          <div className="flex-1">
            <SearchInput
              placeholder="Search across all columns (asset name, ID, stage, owner)..."
              value={globalFilter ?? ""}
              onChange={(e) => setGlobalFilter(e.target.value)}
              showClear
              onClear={() => setGlobalFilter("")}
              className="h-8.5 text-xs"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
            {/* TYPE FILTER PILLS (MATCHED STRICTLY WITH REGISTER PAGE MODALITIES) */}
            <div className="flex items-center gap-1 bg-muted p-0.5 rounded-lg border border-border/50 shrink-0">
              {registerModalities.map((item) => (
                <button
                  key={item.value}
                  onClick={() => setSelectedType(item.value)}
                  className={`px-2.5 py-1 text-xs rounded-md font-medium transition-all ${
                    selectedType.toLowerCase() === item.value.toLowerCase()
                      ? "bg-background text-foreground shadow-xs border border-border/40"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {/* STATUS FILTER USING SHADCN SELECT UI COMPONENT */}
            <div className="shrink-0">
              <Select
                value={selectedStatus}
                onValueChange={(val) => {
                  if (typeof val === "string") setSelectedStatus(val);
                }}
              >
                <SelectTrigger className="h-8 text-xs min-w-[130px] bg-background">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {statusOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0 flex flex-col justify-between">
        <div className="overflow-x-auto min-h-[360px]">
          <Table className="w-full table-fixed min-w-[720px]">
            <TableHeader className="bg-muted/50 dark:bg-zinc-900/50">
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id} className="hover:bg-transparent">
                  {headerGroup.headers.map((header) => {
                    const widthClass =
                      columnWidths[header.id] || "w-auto";
                    return (
                      <TableHead
                        key={header.id}
                        className={`font-semibold text-foreground text-xs h-10 px-3 border-r border-border/40 last:border-r-0 ${widthClass}`}
                      >
                        {header.isPlaceholder ? null : (
                          <table.FlexRender header={header} />
                        )}
                      </TableHead>
                    );
                  })}
                </TableRow>
              ))}
            </TableHeader>

            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    className="hover:bg-muted/30 transition-colors h-14"
                  >
                    {row.getVisibleCells().map((cell) => {
                      const widthClass =
                        columnWidths[cell.column.id] || "w-auto";
                      return (
                        <TableCell
                          key={cell.id}
                          className={`py-2.5 px-3 border-r border-border/30 last:border-r-0 ${widthClass} overflow-hidden`}
                        >
                          <table.FlexRender cell={cell} />
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))
              ) : (
                <TableRow className="hover:bg-transparent">
                  <TableCell
                    colSpan={processingMonitorColumns.length}
                    className="h-64 text-center text-xs text-muted-foreground"
                  >
                    No processing assets match your search criteria.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* PAGINATION CONTROLS */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border/40 bg-card">
          <div className="text-xs text-muted-foreground">
            Page {table.state.pagination.pageIndex + 1} of{" "}
            {table.getPageCount() || 1}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="h-7 text-xs px-2.5"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="h-7 text-xs px-2.5"
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
