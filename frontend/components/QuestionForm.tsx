"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sliders, RefreshCw } from "lucide-react";

interface Props {
  onSubmit: (question: string, topK: number) => Promise<void>;
  loading: boolean;
}

const SUGGESTIONS = [
  "How many days of annual leave do I get?",
  "What is the remote work policy?",
  "How does the performance review process work?",
  "What are the expense reimbursement limits?",
  "What security practices should I follow?",
];

export default function QuestionForm({ onSubmit, loading }: Props) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(4);
  const [showSettings, setShowSettings] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    await onSubmit(q, topK);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {/* Suggestions */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setQuestion(s)}
            className="text-xs px-3 py-1.5 rounded-full border border-slate-700/70 text-slate-500 hover:text-slate-300 hover:border-slate-600 transition-all bg-slate-900/50 truncate max-w-[260px]"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="relative rounded-xl border border-slate-700 bg-slate-900 focus-within:border-indigo-500/60 focus-within:glow-indigo transition-all">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about company policy, benefits, leave, or HR procedures…"
          rows={2}
          maxLength={1000}
          className="w-full bg-transparent px-4 pt-4 pb-12 text-sm text-slate-100 placeholder-slate-600 resize-none focus:outline-none leading-relaxed"
        />

        {/* Toolbar */}
        <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowSettings((v) => !v)}
              className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border transition-all ${
                showSettings
                  ? "border-indigo-500/40 text-indigo-300 bg-indigo-500/10"
                  : "border-slate-700 text-slate-500 hover:text-slate-300 hover:border-slate-600"
              }`}
            >
              <Sliders className="w-3 h-3" />
              <span>Sources: {topK}</span>
            </button>

            {question.length > 0 && (
              <button
                type="button"
                onClick={() => setQuestion("")}
                className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 text-slate-500 hover:text-slate-300 hover:border-slate-600 transition-all"
              >
                <RefreshCw className="w-3 h-3" />
                Clear
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-700 tabular-nums">{question.length}/1000</span>
            <button
              type="submit"
              disabled={loading || question.trim().length < 3}
              className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-all active:scale-95"
            >
              {loading ? (
                <>
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </>
              ) : (
                <>
                  <span>Ask</span>
                  <Send className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Settings drawer */}
      {showSettings && (
        <div className="animate-fade-in rounded-lg border border-slate-800 bg-slate-900/60 p-4">
          <label className="flex items-center justify-between text-sm text-slate-400">
            <div>
              <p className="font-medium text-slate-300">Source chunks</p>
              <p className="text-xs text-slate-600 mt-0.5">Number of handbook excerpts to retrieve (1–10)</p>
            </div>
            <span className="text-indigo-300 font-semibold w-6 text-right">{topK}</span>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="mt-3 w-full accent-indigo-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-700 mt-1">
            <span>1 (fast)</span>
            <span>10 (thorough)</span>
          </div>
        </div>
      )}
    </form>
  );
}
