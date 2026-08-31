"use client";

import React from "react";
import { Recommendation } from "@/types";
import { Spinner } from "@/components/ui/spinner";
import { RecommendationCard } from "./recommendation-card";

interface RecommendationsGridProps {
  recommendations: Recommendation[];
  isLoading: boolean;
  searchQuery?: string;
  onSelectRecommendation: (item: Recommendation) => void;
}

export function RecommendationsGrid({
  recommendations,
  isLoading,
  searchQuery = "",
  onSelectRecommendation,
}: RecommendationsGridProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 gap-2 text-sm text-muted-foreground">
        <Spinner className="h-4 w-4 text-muted-foreground" />
        <span>Loading curated recommendations...</span>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="text-center py-16 text-sm text-muted-foreground">
        {searchQuery
          ? "No recommendations match your search."
          : "No curated recommendations yet. Use the chat to generate insights and add them here."}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {recommendations.map((item) => (
        <RecommendationCard
          key={item.id}
          item={item}
          onSelect={onSelectRecommendation}
        />
      ))}
    </div>
  );
}
