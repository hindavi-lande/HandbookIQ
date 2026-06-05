"use client";

import { useEffect, useState } from "react";
import { Sparkles, AlertCircle, MessageSquarePlus } from "lucide-react";
import QuestionForm from "@/components/QuestionForm";
import AnswerPanel from "@/components/AnswerPanel";
import { api } from "@/lib/api";
import {
  clearStoredSessionId,
  createSessionId,
  getOrCreateSessionId,
  storeSessionId,
} from "@/lib/session";
import type { AskResponse } from "@/types";

export default function HomePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = getOrCreateSessionId();
    setSessionId(id);
    storeSessionId(id);
  }, []);

  const handleAsk = async (question: string, topK: number) => {
    const activeSessionId = sessionId ?? getOrCreateSessionId();
    setLoading(true);
    setError(null);
    try {
      const res = await api.ask({
        question,
        top_k: topK,
        session_id: activeSessionId,
      });
      const resolvedSessionId = res.session_id ?? activeSessionId;
      setSessionId(resolvedSessionId);
      storeSessionId(resolvedSessionId);
      setResponse(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    const newSessionId = createSessionId();
    clearStoredSessionId();
    storeSessionId(newSessionId);
    setSessionId(newSessionId);
    setResponse(null);
    setError(null);
  };

  return (
    <div className="bg-grid min-h-[calc(100vh-64px)]">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-8">
        {/* Hero */}
        <div className="text-center space-y-3 pt-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/25 bg-indigo-500/10 text-indigo-300 text-xs font-medium mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Employee Handbook · AI-Powered Q&A
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
            <span className="text-gradient">Ask HandbookIQ</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
            Get instant, accurate answers from the official employee handbook — leaves, benefits, remote
            work, security, and more.
          </p>
        </div>

        {/* Question Form */}
        <div className="space-y-3">
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleNewConversation}
              disabled={loading}
              className="inline-flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-500 hover:text-slate-300 hover:border-slate-600 transition-all disabled:opacity-40"
            >
              <MessageSquarePlus className="w-3.5 h-3.5" />
              New conversation
            </button>
          </div>
          <QuestionForm onSubmit={handleAsk} loading={loading} />
        </div>

        {/* Error */}
        {error && (
          <div className="animate-fade-in flex items-start gap-3 rounded-xl border border-red-800/50 bg-red-950/30 px-4 py-3.5 text-sm text-red-400">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-red-300">Request failed</p>
              <p className="text-red-500 text-xs mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="animate-pulse rounded-xl border border-slate-800 bg-slate-900/80 p-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-slate-800" />
              <div className="h-4 w-40 rounded bg-slate-800" />
              <div className="ml-auto h-3 w-24 rounded bg-slate-800" />
            </div>
            <div className="space-y-2 pt-2">
              <div className="h-3 rounded bg-slate-800 w-full" />
              <div className="h-3 rounded bg-slate-800 w-5/6" />
              <div className="h-3 rounded bg-slate-800 w-4/6" />
            </div>
            <div className="flex gap-1.5 pt-2">
              <span className="loading-dot" />
              <span className="loading-dot" />
              <span className="loading-dot" />
            </div>
          </div>
        )}

        {/* Answer */}
        {!loading && response && <AnswerPanel response={response} />}
      </div>
    </div>
  );
}
