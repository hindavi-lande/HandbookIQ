"use client";

import { useEffect, useState } from "react";
import { History, ChevronDown, ChevronUp, RefreshCw, Search, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { HistoryItem } from "@/types";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function HistoryRow({ item }: { item: HistoryItem }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden hover:border-slate-700 transition-colors bg-slate-900/50">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-start gap-3 px-4 py-3.5 text-left"
      >
        <div className="mt-0.5 w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="text-sm text-slate-200 font-medium leading-snug">{item.question}</p>
          {!expanded && (
            <p className="text-xs text-slate-600 mt-1 line-clamp-1">{item.answer}</p>
          )}
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className="text-xs text-slate-600 tabular-nums">{timeAgo(item.created_at)}</span>
          {expanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-600" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-600" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="border-t border-slate-800 px-4 py-3.5 bg-slate-950/50 animate-fade-in">
          <p className="text-sm text-slate-400 leading-relaxed">{item.answer}</p>
          {item.session_id && (
            <p className="mt-2 text-[10px] text-slate-700 font-mono">
              Session: {item.session_id}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.history(100);
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = items.filter(
    (item) =>
      item.question.toLowerCase().includes(search.toLowerCase()) ||
      item.answer.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
            <History className="w-4.5 h-4.5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100">Q&A History</h1>
            <p className="text-xs text-slate-500">{items.length} interactions logged</p>
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600 text-sm transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-5">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search questions and answers…"
          className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-lg border border-slate-800 bg-slate-900/50 p-4 h-16" />
          ))}
        </div>
      ) : error ? (
        <div className="flex items-center gap-3 rounded-xl border border-red-800/50 bg-red-950/30 px-4 py-3.5 text-sm text-red-400">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <p>{error}</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-600">
          <History className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">{search ? "No matching results" : "No history yet. Ask a question first!"}</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((item) => (
            <HistoryRow key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
