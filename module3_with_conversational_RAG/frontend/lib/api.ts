import type {
  AskRequest,
  AskResponse,
  HistoryItem,
  DocumentMeta,
  IngestResponse,
  HealthResponse,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  ask(body: AskRequest) {
    return request<AskResponse>("/api/ask", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  history(limit = 50) {
    return request<HistoryItem[]>(`/api/history?limit=${limit}`);
  },

  documents() {
    return request<DocumentMeta[]>("/api/documents");
  },

  ingest(directory?: string) {
    return request<IngestResponse>("/api/ingest", {
      method: "POST",
      body: JSON.stringify({ directory: directory || null }),
    });
  },

  health() {
    return request<HealthResponse>("/health");
  },
};
