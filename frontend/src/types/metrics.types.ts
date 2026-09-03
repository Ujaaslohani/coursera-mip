// METRICS API RESPONSE INTERFACE (QDRANT DATABASE COLLECTION METRICS)
export interface MetricsResponse {
  collection_name: string;
  qdrant_status: string | null;
  points_count: number | null;
  scanned_records: number;
  content_type_counts: Record<string, number>;
  course_id_counts: Record<string, number>;
  embedding_model_counts: Record<string, number>;
}
