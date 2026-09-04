"use client";

import React from "react";
import { SearchInput } from "@/components/ui/search-input";

interface RecommendationsToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
}

export function RecommendationsToolbar({
  searchQuery,
  onSearchChange,
}: RecommendationsToolbarProps) {
  return (
    <div className="w-full bg-card">
      <SearchInput
        placeholder="Search recommendations..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        showClear
        onClear={() => onSearchChange("")}
        className="h-9 text-sm"
      />
    </div>
  );
}
