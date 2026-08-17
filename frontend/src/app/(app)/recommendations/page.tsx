"use client";

import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { Recommendation } from "@/types";
import { mockRecommendations } from "@/temp-data/recommendations-data";
import { RefreshCw } from "lucide-react";
import { RecommendationCard } from "./recommendation-card";
import { RecommendationSheet } from "./recommendation-sheet";

export default function RecommendationsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] =
    useState<Recommendation[]>(mockRecommendations);
  const [selectedRecommendation, setSelectedRecommendation] =
    useState<Recommendation | null>(null);
  const [noteText, setNoteText] = useState("");

  // TODO: IMPLEMENT THE BACKEND API
  const handleLoad = () => {};

  const handleSelectRecommendation = (item: Recommendation) => {
    setSelectedRecommendation(item);
    setNoteText(item.note || "");
  };

  // TODO: IMPLEMENT THE BACKEND API
  const handleAccept = () => {};

  // TODO: IMPLEMENT THE BACKEND API
  const handleReject = () => {};

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
          onClick={handleLoad}
          disabled={isLoading}
          className="h-9 gap-1.5 px-4 shrink-0"
        >
          <RefreshCw
            className={isLoading ? "h-4 w-4 animate-spin" : "h-4 w-4"}
          />
          {isLoading ? "Loading..." : "Load"}
        </Button>
      </div>

      {/* RECOMMENDATIONS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRecommendations.map((item) => (
          <RecommendationCard
            key={item.id}
            item={item}
            onSelect={handleSelectRecommendation}
          />
        ))}
      </div>

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
