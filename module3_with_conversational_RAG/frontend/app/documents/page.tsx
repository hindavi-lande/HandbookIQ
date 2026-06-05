"use client";

import { useEffect, useState } from "react";
import {
  FolderOpen,
  RefreshCw,
  Upload,
  FileText,
  Layers,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { api } from "@/lib/api";
import type { DocumentMeta, IngestResponse } from "@/types";

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function DocumentCard({ doc }: { doc: DocumentMeta }) {
  return (
    <div className="flex items-center gap-4 px-4 py-3.5 rounded-lg border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-colors">
      <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
        <FileText className="w-4 h-4 text-indigo-400" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-200 truncate">{doc.filename}</p>
        <p className="text-xs text-slate-600 mt-0.5 truncate">{doc.file_path}</p>
      </div>
      <div className="text-right shrink-0 space-y-0.5">
        <div className="flex items-center gap-1.5 text-cyan-400">
          <Layers className="w-3 h-3" />
          <span className="text-xs font-semibold tabular-nums">{doc.chunk_count} chunks</span>
        </div>
        <p className="text-[10px] text-slate-600">{formatDate(doc.ingested_at)}</p>
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [docsError, setDocsError] = useState<string | null>(null);

  const [directory, setDirectory] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const [showChunks, setShowChunks] = useState(false);

  const loadDocs = async () => {
    setLoadingDocs(true);
    setDocsError(null);
    try {
      setDocs(await api.documents());
    } catch (e) {
      setDocsError(e instanceof Error ? e.message : "Failed to load documents");
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => { loadDocs(); }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngesting(true);
    setIngestError(null);
    setIngestResult(null);
    try {
      const res = await api.ingest(directory.trim() || undefined);
      setIngestResult(res);
      await loadDocs();
    } catch (e) {
      setIngestError(e instanceof Error ? e.message : "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      {/* Ingest Panel */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden">
        <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Upload className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Ingest Documents</h2>
            <p className="text-xs text-slate-500">
              Load .txt and .pdf files into the vector store
            </p>
          </div>
        </div>

        <form onSubmit={handleIngest} className="p-5 space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1.5">
              Directory path{" "}
              <span className="text-slate-600 font-normal">(leave blank for default: data/handbook/)</span>
            </label>
            <input
              value={directory}
              onChange={(e) => setDirectory(e.target.value)}
              placeholder="/path/to/your/documents"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 transition-colors font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={ingesting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-all active:scale-95"
          >
            {ingesting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Ingesting…
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Start Ingestion
              </>
            )}
          </button>
        </form>

        {/* Ingest Error */}
        {ingestError && (
          <div className="mx-5 mb-5 flex items-start gap-3 rounded-lg border border-red-800/50 bg-red-950/30 px-4 py-3 text-sm text-red-400 animate-fade-in">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <p>{ingestError}</p>
          </div>
        )}

        {/* Ingest Success */}
        {ingestResult && (
          <div className="mx-5 mb-5 rounded-lg border border-emerald-800/50 bg-emerald-950/30 animate-fade-in overflow-hidden">
            <div className="flex items-center gap-3 px-4 py-3">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
              <p className="text-sm text-emerald-300 font-medium">{ingestResult.message}</p>
              <button
                type="button"
                onClick={() => setShowChunks((v) => !v)}
                className="ml-auto flex items-center gap-1 text-xs text-emerald-600 hover:text-emerald-400"
              >
                Details
                {showChunks ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            </div>
            {showChunks && (
              <div className="border-t border-emerald-900/50 px-4 py-3 max-h-48 overflow-y-auto animate-fade-in">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {ingestResult.chunks.map((c) => (
                    <div
                      key={c.chunk_id}
                      className="text-[10px] font-mono text-emerald-700 bg-emerald-950/40 rounded px-2 py-1"
                    >
                      [{c.chunk_index}] {c.source_file} · {c.char_count}c
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
              <FolderOpen className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100">Ingested Documents</h2>
              <p className="text-xs text-slate-500">{docs.length} documents in vector store</p>
            </div>
          </div>
          <button
            onClick={loadDocs}
            disabled={loadingDocs}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600 text-sm transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingDocs ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {loadingDocs ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse h-16 rounded-lg border border-slate-800 bg-slate-900/60" />
            ))}
          </div>
        ) : docsError ? (
          <div className="flex items-center gap-3 rounded-xl border border-red-800/50 bg-red-950/30 px-4 py-3.5 text-sm text-red-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <p>{docsError}</p>
          </div>
        ) : docs.length === 0 ? (
          <div className="text-center py-16 text-slate-700">
            <FolderOpen className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No documents ingested yet.</p>
            <p className="text-xs mt-1">Use the panel above to load handbook files.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {docs.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
