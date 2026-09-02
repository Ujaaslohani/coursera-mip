"use client";

import React, { useState, useMemo } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Recommendation } from "@/types";
import { useRecommendations } from "@/hooks/query/use-recommendations";
import { useReviewFeedback } from "@/hooks/mutations/use-review-feedback";
import {
  mapToRecommendation,
  filterRecommendations,
} from "@/components/recommendations/recommendation-mapper";
import { RecommendationsToolbar } from "@/components/recommendations/recommendations-toolbar";
import { RecommendationsGrid } from "@/components/recommendations/recommendations-grid";
import { RecommendationSheet } from "@/components/recommendations/recommendation-sheet";

export default function RecommendationsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRecommendation, setSelectedRecommendation] =
    useState<Recommendation | null>(null);
  const [noteText, setNoteText] = useState("");

  const {
    data: rawRecommendations = [],
    isLoading,
    isFetching,
    refetch,
  } = useRecommendations(50);

  const reviewFeedback = useReviewFeedback();

  // Map raw Supabase rows to typed Recommendation objects
  const recommendations: Recommendation[] = useMemo(
    () => rawRecommendations.map(mapToRecommendation),
    [rawRecommendations]
  );

  // Filter recommendations by search query
  const filteredRecommendations = useMemo(
    () => filterRecommendations(recommendations, searchQuery),
    [recommendations, searchQuery]
  );

  const handleSelectRecommendation = (item: Recommendation) => {
    console.log("[Recommendations] Selected recommendation:", item);
    setSelectedRecommendation(item);
    setNoteText(item.note || "");
  };

  const handleAccept = () => {
    if (!selectedRecommendation || reviewFeedback.isPending) return;
    console.log("[Recommendations] Accepting recommendation:", {
      id: selectedRecommendation.id,
      notes: noteText,
    });
    reviewFeedback.mutate(
      {
        response_id: selectedRecommendation.id,
        decision: "accepted",
        notes: noteText || undefined,
      },
      {
        onSuccess: () => setSelectedRecommendation(null),
      }
    );
  };

  const handleReject = () => {
    if (!selectedRecommendation || reviewFeedback.isPending) return;
    console.log("[Recommendations] Rejecting recommendation:", {
      id: selectedRecommendation.id,
      notes: noteText,
    });
    reviewFeedback.mutate(
      {
        response_id: selectedRecommendation.id,
        decision: "rejected",
        notes: noteText || undefined,
      },
      {
        onSuccess: () => setSelectedRecommendation(null),
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recommendations"
        description="Multimodal content suggestions curated using student telemetry and curriculum alignment."
      />

      {/* FILTER AND SEARCH BAR */}
      <RecommendationsToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onRefresh={() => refetch()}
        isLoading={isLoading || isFetching}
      />

      {/* RECOMMENDATIONS GRID / LOADING / EMPTY STATES */}
      <RecommendationsGrid
        recommendations={filteredRecommendations}
        isLoading={isLoading}
        searchQuery={searchQuery}
        onSelectRecommendation={handleSelectRecommendation}
      />

      {/* SELECTED RECOMMENDATION DETAIL SHEET */}
      <RecommendationSheet
        selectedRecommendation={selectedRecommendation}
        onOpenChange={(open) => {
          if (!open) setSelectedRecommendation(null);
        }}
        noteText={noteText}
        onNoteChange={setNoteText}
        onAccept={handleAccept}
        onReject={handleReject}
      />
    </div>
  );
}
