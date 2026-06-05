import { Bot, Clock, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import SourceCard from "./SourceCard";
import type { AskResponse } from "@/types";

interface Props {
  response: AskResponse;
}

export default function AnswerPanel({ response }: Props) {
  const [showSources, setShowSources] = useState(true);

  const formattedDate = new Date(response.created_at).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const paragraphs = response.answer.split(/\n+/).filter(Boolean);

  return (
    <div className="animate-slide-up rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3.5 border-b border-slate-800 bg-slate-900">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500/30 to-cyan-500/30 border border-indigo-500/30 flex items-center justify-center">
          <Bot className="w-4 h-4 text-indigo-300" />
        </div>
        <span className="text-sm font-semibold text-slate-200">HandbookIQ Response</span>
        <div className="ml-auto flex items-center gap-1.5 text-xs text-slate-500">
          <Clock className="w-3 h-3" />
          <span>{formattedDate}</span>
        </div>
      </div>

      {/* Answer */}
      <div className="px-5 py-4">
        <div className="answer-text text-sm text-slate-300 leading-relaxed">
          {paragraphs.map((para, i) => (
            <p key={i}>{para}</p>
          ))}
        </div>
      </div>

      {/* Sources */}
      {response.sources.length > 0 && (
        <div className="border-t border-slate-800">
          <button
            onClick={() => setShowSources((v) => !v)}
            className="w-full flex items-center justify-between px-5 py-3 text-xs font-semibold text-slate-500 hover:text-slate-300 transition-colors"
          >
            <span className="uppercase tracking-wider">
              Sources · {response.sources.length} chunks retrieved
            </span>
            {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showSources && (
            <div className="px-5 pb-4 grid grid-cols-1 sm:grid-cols-2 gap-2 animate-fade-in">
              {response.sources.map((src, i) => (
                <SourceCard key={src.chunk_id} source={src} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
