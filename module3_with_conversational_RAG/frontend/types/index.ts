export interface SourceChunk {
  chunk_id: string;
  source_file: string;
  score: number;
  excerpt: string;
}

export interface AskRequest {
  question: string;
  top_k?: number;
  session_id?: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: SourceChunk[];
  session_id: string | null;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  session_id: string | null;
  question: string;
  answer: string;
  created_at: string;
}

export interface DocumentMeta {
  id: string;
  filename: string;
  file_path: string;
  chunk_count: number;
  ingested_at: string;
}

export interface ChunkMeta {
  chunk_id: string;
  source_file: string;
  chunk_index: number;
  char_count: number;
}

export interface IngestResponse {
  message: string;
  total_chunks: number;
  chunks: ChunkMeta[];
}

export interface HealthResponse {
  status: "ok" | "degraded";
  postgres: string;
  qdrant: string;
  collection: string;
}
