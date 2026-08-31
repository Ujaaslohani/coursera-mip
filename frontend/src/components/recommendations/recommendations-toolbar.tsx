"use client";

import React from "react";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";

interface RecommendationsToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export function RecommendationsToolbar({
  searchQuery,
  onSearchChange,
  onRefresh,
  isLoading,
}: RecommendationsToolbarProps) {
  return (
    <div className="flex items-center gap-2 w-full bg-card">
      <SearchInput
        placeholder="Search recommendations..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        showClear
        onClear={() => onSearchChange("")}
        className="h-9 text-sm"
      />
      <Button
        onClick={onRefresh}
        disabled={isLoading}
        className="h-9 gap-1.5 px-4 shrink-0 cursor-pointer"
      >
        {isLoading ? (
          <Spinner className="h-4 w-4 text-muted-foreground" />
        ) : (
          <RefreshCw className="h-4 w-4" />
        )}
        {isLoading ? "Loading..." : "Refresh"}
      </Button>
    </div>
  );
}
