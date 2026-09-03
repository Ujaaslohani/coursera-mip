import { Recommendation } from "@/types";

/**
 * MAPS A RAW SUPABASE RECOMMENDATION ROW TO THE FRONTEND RECOMMENDATION SHAPE.
 */
export function mapToRecommendation(raw: any): Recommendation {
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
    status:
      generatedResponse.response_status === "pending"
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

/**
 * FILTERS A LIST OF RECOMMENDATIONS BY SEARCH QUERY STRING.
 */
export function filterRecommendations(
  recommendations: Recommendation[],
  searchQuery: string
): Recommendation[] {
  if (!searchQuery.trim()) return recommendations;

  const query = searchQuery.toLowerCase().trim();
  return recommendations.filter(
    (item) =>
      item.title.toLowerCase().includes(query) ||
      item.queryBy.toLowerCase().includes(query) ||
      item.category.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
  );
}
