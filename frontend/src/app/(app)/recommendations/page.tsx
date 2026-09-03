"use client";

import React, { useState, useMemo, useEffect } from "react";
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

const PAGE_SIZE = 12;

export default function RecommendationsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const [selectedRecommendation, setSelectedRecommendation] =
    useState<Recommendation | null>(null);
  const [noteText, setNoteText] = useState("");

  // RESET TO PAGE 0 WHENEVER SEARCH CHANGES
  useEffect(() => {
    setPage(0);
  }, [searchQuery]);

  const {
    data: rawRecommendations = [],
    isLoading,
    isFetching,
    refetch,
  } = useRecommendations({ page, pageSize: PAGE_SIZE });

  const reviewFeedback = useReviewFeedback();

  // MAP RAW SUPABASE ROWS TO TYPED RECOMMENDATION OBJECTS
  const recommendations: Recommendation[] = useMemo(
    () => rawRecommendations.map(mapToRecommendation),
    [rawRecommendations]
  );

  // CLIENT-SIDE FILTER WITHIN THE CURRENT PAGE (FAST — ONLY 12 ITEMS)
  const filteredRecommendations = useMemo(
    () => filterRecommendations(recommendations, searchQuery),
    [recommendations, searchQuery]
  );

  // HEURISTIC: IF WE GOT A FULL PAGE BACK, THERE'S PROBABLY A NEXT PAGE
  const hasNextPage = rawRecommendations.length === PAGE_SIZE;
  const hasPrevPage = page > 0;

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

      {/* FILTER / SEARCH BAR + PAGINATION CONTROLS */}
      <RecommendationsToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onRefresh={() => refetch()}
        isLoading={isLoading || isFetching}
        page={page}
        pageSize={PAGE_SIZE}
        totalOnPage={rawRecommendations.length}
        hasPrevPage={hasPrevPage}
        hasNextPage={hasNextPage}
        onPageChange={setPage}
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
