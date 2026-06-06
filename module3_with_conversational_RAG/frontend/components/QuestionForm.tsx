"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sliders, RefreshCw } from "lucide-react";
import type { ProviderOption } from "@/types";

interface Props {
  onSubmit: (
    question: string,
    topK: number,
    llmProvider: string,
    modelName: string
  ) => Promise<void>;
  loading: boolean;
  providers: ProviderOption[];
  llmProvider: string;
  modelName: string;
  onLlmChange: (provider: string, model: string) => void;
}

const SUGGESTIONS = [
  "How many days of annual leave do I get?",
  "What is the remote work policy?",
  "How does the performance review process work?",
  "What are the expense reimbursement limits?",
  "What security practices should I follow?",
];

export default function QuestionForm({
  onSubmit,
  loading,
  providers,
  llmProvider,
  modelName,
  onLlmChange,
}: Props) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(4);
  const [showSettings, setShowSettings] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const activeProvider =
    providers.find((provider) => provider.id === llmProvider) ?? providers[0];
  const availableModels = activeProvider?.models ?? [];

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading || !llmProvider || !modelName) return;
    await onSubmit(q, topK, llmProvider, modelName);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const handleProviderChange = (providerId: string) => {
    const provider = providers.find((item) => item.id === providerId);
    if (!provider) return;
    onLlmChange(providerId, provider.default_model);
  };

  const selectedModelLabel =
    availableModels.find((model) => model.id === modelName)?.label ?? modelName;

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
              <span>
                {activeProvider?.label ?? "Model"} · {selectedModelLabel}
              </span>
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
              disabled={loading || question.trim().length < 3 || !llmProvider || !modelName}
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
        <div className="animate-fade-in rounded-lg border border-slate-800 bg-slate-900/60 p-4 space-y-5">
          {providers.length > 0 && (
            <div className="space-y-3">
              <div>
                <p className="font-medium text-slate-300 text-sm">LLM provider</p>
                <p className="text-xs text-slate-600 mt-0.5">
                  Switch between cloud and local models for each question
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {providers.map((provider) => (
                  <button
                    key={provider.id}
                    type="button"
                    onClick={() => handleProviderChange(provider.id)}
                    className={`rounded-lg border px-3 py-2 text-left text-xs transition-all ${
                      llmProvider === provider.id
                        ? "border-indigo-500/40 bg-indigo-500/10 text-indigo-200"
                        : "border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-300"
                    }`}
                  >
                    <span className="block font-medium">{provider.label}</span>
                  </button>
                ))}
              </div>
              <label className="block text-xs text-slate-500">
                Model
                <select
                  value={modelName}
                  onChange={(e) => onLlmChange(llmProvider, e.target.value)}
                  className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-indigo-500/60 focus:outline-none"
                >
                  {availableModels.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}

          <div>
            <label className="flex items-center justify-between text-sm text-slate-400">
              <div>
                <p className="font-medium text-slate-300">Source chunks</p>
                <p className="text-xs text-slate-600 mt-0.5">
                  Number of handbook excerpts to retrieve (1–10)
                </p>
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
        </div>
      )}
    </form>
  );
}
