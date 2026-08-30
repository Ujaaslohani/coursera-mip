import { type ChatMessage } from "@/types/chat.types";

export interface ConversationHistoryItem {
  id: string;
  title: string;
  timestamp: string;
  preview: string;
}

export function formatTimeAgo(isoString?: string | null): string {
  if (!isoString) return "Recently";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return "Recently";
  }
}

export function formatServerMessages(serverMessages: any[]): ChatMessage[] {
  const formatted: ChatMessage[] = [];
  serverMessages.forEach((query) => {
    formatted.push({ role: "user", content: query.query_text });

    if (query.generated_responses && query.generated_responses.length > 0) {
      const response = query.generated_responses[0];
      formatted.push({
        role: "assistant",
        content: response.generated_answer,
        insightId: response.response_id,
        confidence: 0.9,
        citations:
          response.retrieval_evidence?.map((e: any) => ({
            point_id: e.qdrant_record_id,
            content_type: e.content_type,
            lecture_id: e.lecture_id,
            score: e.similarity_score,
            text_preview: e.evidence_text,
          })) || [],
        recommendedAction:
          response.recommendations?.length > 0
            ? response.recommendations[0].recommendation_text
            : null,
        isCurated:
          response.response_status === "pending" ||
          response.response_status === "curated",
        curatedSteps:
          response.recommendations?.map((r: any) => r.recommendation_text) || [],
      });
    }
  });
  return formatted;
}

export function mapServerConversations(
  serverConversations: any[]
): ConversationHistoryItem[] {
  return serverConversations.map((c) => ({
    id: c.conversation_id,
    title: c.title || `Conversation ${c.conversation_id.slice(0, 8)}`,
    timestamp: formatTimeAgo(c.last_activity_at || c.started_at),
    preview: c.session_id
      ? `Session: ${c.session_id}`
      : "Course learning analytics query",
  }));
}
