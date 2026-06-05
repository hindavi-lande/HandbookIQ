"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, History, FolderOpen, Zap } from "lucide-react";
import HealthBadge from "./HealthBadge";

const navItems = [
  { href: "/", label: "Ask", icon: BookOpen },
  { href: "/history", label: "History", icon: History },
  { href: "/documents", label: "Documents", icon: FolderOpen },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-800/60 bg-[#020817]/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg">
            <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-bold text-slate-100 text-sm tracking-tight">HandbookIQ</span>
            <span className="text-[10px] text-slate-500 tracking-widest uppercase">Handbook Assistant</span>
          </div>
        </Link>

        {/* Nav Links */}
        <div className="flex items-center gap-0.5">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                  active
                    ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/25"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/70"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </div>

        {/* Health */}
        <div className="shrink-0">
          <HealthBadge />
        </div>
      </div>
    </nav>
  );
}
