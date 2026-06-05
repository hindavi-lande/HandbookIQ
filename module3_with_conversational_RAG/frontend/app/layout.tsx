import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "HandbookIQ — Employee Handbook Assistant",
  description: "HandbookIQ — AI-powered Q&A portal for company policies and employee handbook",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#020817] text-slate-100 antialiased">
        <Navbar />
        <main className="min-h-[calc(100vh-64px)]">{children}</main>
        <footer className="border-t border-slate-800/60 py-4 mt-8">
          <p className="text-center text-xs text-slate-700">
            HandbookIQ · Internal use only · Powered by RAG + Groq
          </p>
        </footer>
      </body>
    </html>
  );
}
