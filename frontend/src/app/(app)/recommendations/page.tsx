"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { Recommendation } from "@/types";
import { useRecommendations } from "@/hooks/query/use-recommendations";
import { useQueryClient } from "@tanstack/react-query";
import api from "@/api/axios";
import { RefreshCw, Loader } from "lucide-react";
import { RecommendationCard } from "@/components/recommendations/recommendation-card";
import { RecommendationSheet } from "@/components/recommendations/recommendation-sheet";

/**
 * Maps a raw Supabase recommendation row to the frontend Recommendation shape.
 */
function mapToRecommendation(raw: any): Recommendation {
  const metadata = raw.metadata || {};
  const generatedResponse = raw.generated_responses || {};
  const userQuery = generatedResponse.user_queries || {};
  const evidenceList: any[] = generatedResponse.retrieval_evidence || [];

  return {
    id: raw.recommendation_id || raw.id || "",
    title: metadata.title || raw.recommendation_text?.slice(0, 80) || "Untitled",
    queryBy: userQuery.query_text || "system",
    category: raw.recommendation_type || "content_review",
    description: raw.recommendation_text || "",
    timestamp: raw.created_at
      ? new Date(raw.created_at).toLocaleDateString()
      : "Recently",
    status: generatedResponse.response_status === "pending"
      ? "pending"
      : generatedResponse.response_status === "accepted"
        ? "applied"
        : generatedResponse.response_status === "rejected"
          ? "rejected"
          : "curated",
    suggestedAction: raw.recommendation_text,
    citations: evidenceList.map((ev: any) => ({
      id: ev.qdrant_record_id || "",
      type: ev.content_type || "transcript",
      quote: ev.evidence_text || "",
      explanation: `Relevance: ${Math.round((ev.similarity_score || 0) * 100)}% • Rank #${ev.retrieval_rank || "—"}`,
    })),
  };
}

export default function RecommendationsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRecommendation, setSelectedRecommendation] =
    useState<Recommendation | null>(null);
  const [noteText, setNoteText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const queryClient = useQueryClient();
  const {
    data: rawRecommendations = [],
    isLoading,
    isFetching,
    refetch,
  } = useRecommendations(50);

  // Map raw Supabase rows to Recommendation shape
  const recommendations: Recommendation[] = rawRecommendations.map(mapToRecommendation);

  const handleSelectRecommendation = (item: Recommendation) => {
    setSelectedRecommendation(item);
    setNoteText(item.note || "");
  };

  const handleAccept = async () => {
    if (!selectedRecommendation || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await api.post("/api/review-feedback", {
        response_id: selectedRecommendation.id,
        decision: "accepted",
        notes: noteText || undefined,
      });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      setSelectedRecommendation(null);
    } catch (err) {
      console.error("Failed to accept recommendation:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!selectedRecommendation || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await api.post("/api/review-feedback", {
        response_id: selectedRecommendation.id,
        decision: "rejected",
        notes: noteText || undefined,
      });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      setSelectedRecommendation(null);
    } catch (err) {
      console.error("Failed to reject recommendation:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredRecommendations = recommendations.filter((item) => {
    const query = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(query) ||
      item.queryBy.toLowerCase().includes(query) ||
      item.category.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    );
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recommendations"
        description="Multimodal content suggestions curated using student telemetry and curriculum alignment."
      />

      {/* FILTER AND SEARCH BAR */}
      <div className="flex items-center gap-2 w-full bg-card">
        <SearchInput
          placeholder="Search recommendations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          showClear
          onClear={() => setSearchQuery("")}
          className="h-9 text-sm"
        />
        <Button
          onClick={() => refetch()}
          disabled={isLoading || isFetching}
          className="h-9 gap-1.5 px-4 shrink-0"
        >
          <RefreshCw
            className={
              isLoading || isFetching
                ? "h-4 w-4 animate-spin"
                : "h-4 w-4"
            }
          />
          {isLoading || isFetching ? "Loading..." : "Refresh"}
        </Button>
      </div>

      {/* LOADING STATE */}
      {isLoading && (
        <div className="flex items-center justify-center py-16 gap-2 text-sm text-muted-foreground">
          <Loader className="h-4 w-4 animate-spin text-primary" />
          <span>Loading curated recommendations...</span>
        </div>
      )}

      {/* EMPTY STATE */}
      {!isLoading && filteredRecommendations.length === 0 && (
        <div className="text-center py-16 text-sm text-muted-foreground">
          {searchQuery
            ? "No recommendations match your search."
            : "No curated recommendations yet. Use the chat to generate insights and add them here."}
        </div>
      )}

      {/* RECOMMENDATIONS GRID */}
      {!isLoading && filteredRecommendations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecommendations.map((item) => (
            <RecommendationCard
              key={item.id}
              item={item}
              onSelect={handleSelectRecommendation}
            />
          ))}
        </div>
      )}

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
