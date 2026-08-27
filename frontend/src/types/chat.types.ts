
// CITATION & EVIDENCE TYPES
export interface Citation {
  point_id: string;
  content_type?: string;
  lecture_id?: string;
  score?: number;
  text_preview: string;
}

// SYNTHESIZE API TYPES (POST /api/synthesize)
export interface SynthesizeRequest {
  query: string;
  conversation_id?: string;
  session_id?: string;
  top_k?: number;
}

export interface SynthesizeResponse {
  insight_id: string;
  conversation_id: string;
  query_id: string;
  answer_text: string;
  citations: Citation[];
  confidence: number;
  status: string;
}

export interface ConversationResponse {
  conversation_id: string;
  session_id?: string | null;
  title?: string | null;
  user_id?: string | null;
  started_at?: string | null;
  last_activity_at?: string | null;
  metadata?: Record<string, any>;
}

// CHAT UI & HISTORY TYPES
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  citations?: Citation[];
}

export interface ChatHistoryItem {
  id: string;
  title: string;
  timestamp: string;
  preview: string;
}

// INSIGHT MESSAGE CARD & PARSER TYPES
export interface InsightMessageCardProps {
  content: string;
  confidence?: number;
  citations?: Citation[];
}

export interface ParsedInsight {
  summary?: string;
  friction?: string;
  action?: string;
  isStructured: boolean;
  rawText: string;
}

export interface ActionStep {
  number: string;
  text: string;
}

export interface ActionData {
  intro: string;
  steps: ActionStep[];
}
