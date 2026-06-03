"use client";

import { useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { api } from "@/lib/api";
import type { HealthResponse } from "@/types";

export default function HealthBadge() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
    const interval = setInterval(() => {
      api.health().then(setHealth).catch(() => setHealth(null));
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  const ok = health?.status === "ok";
  const unknown = health === null;

  return (
    <div
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
        unknown
          ? "border-slate-700 text-slate-500 bg-slate-800/50"
          : ok
          ? "border-emerald-800 text-emerald-400 bg-emerald-950/50"
          : "border-amber-800 text-amber-400 bg-amber-950/50"
      }`}
    >
      <Activity className="w-3 h-3" />
      <span>{unknown ? "Connecting…" : ok ? "All systems go" : "Degraded"}</span>
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          unknown ? "bg-slate-500" : ok ? "bg-emerald-400" : "bg-amber-400"
        } ${ok ? "animate-pulse" : ""}`}
      />
    </div>
  );
}
