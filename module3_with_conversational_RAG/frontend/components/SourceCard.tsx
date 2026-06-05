import { FileText, BarChart2 } from "lucide-react";
import type { SourceChunk } from "@/types";

interface Props {
  source: SourceChunk;
  index: number;
}

export default function SourceCard({ source, index }: Props) {
  const scorePercent = Math.round(source.score * 100);
  const scoreColor =
    source.score >= 0.8
      ? "text-emerald-400"
      : source.score >= 0.6
      ? "text-cyan-400"
      : "text-slate-400";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3.5 space-y-2 hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-[10px] font-bold text-slate-600 bg-slate-800 w-5 h-5 rounded flex items-center justify-center shrink-0">
            {index + 1}
          </span>
          <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
          <span className="text-xs font-medium text-slate-300 truncate">{source.source_file}</span>
        </div>
        <div className={`flex items-center gap-1 shrink-0 ${scoreColor}`}>
          <BarChart2 className="w-3 h-3" />
          <span className="text-xs font-semibold tabular-nums">{scorePercent}%</span>
        </div>
      </div>
      <p className="text-xs text-slate-500 leading-relaxed line-clamp-3">{source.excerpt}</p>
    </div>
  );
}
