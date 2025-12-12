"use client";
import { useEffect, useState } from "react";
import { scriptsApi } from "@/lib/api";
import type { Script } from "@/types";
import Link from "next/link";
import { FileText, Plus, Clock } from "lucide-react";

export default function ScriptsPage() {
  const [scripts, setScripts] = useState<Script[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    scriptsApi.list().then((r) => {
      setScripts(r.data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 bg-surface-card rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Scripts</h1>
          <p className="text-gray-400 text-sm mt-1">Your AI-generated video scripts</p>
        </div>
        <Link
          href="/scripts/new"
          className="bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition"
        >
          <Plus className="w-4 h-4" />
          New Script
        </Link>
      </div>

      {scripts.length === 0 ? (
        <div className="text-center py-16 bg-surface-card rounded-xl border border-surface-border">
          <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <h3 className="text-white font-semibold mb-1">No scripts yet</h3>
          <p className="text-gray-500 text-sm mb-4">Generate your first AI-powered script</p>
          <Link href="/scripts/new" className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm">
            Generate Script
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {scripts.map((script) => (
            <Link
              key={script.id}
              href={`/scripts/${script.id}`}
              className="bg-surface-card border border-surface-border rounded-xl p-4 hover:border-brand-600/30 transition block"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-white font-medium">{script.topic}</h3>
                  <div className="flex items-center gap-4 mt-1">
                    <span className="text-gray-500 text-xs">{script.format_type}</span>
                    <span className="text-gray-500 text-xs flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {script.target_duration_minutes} min
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      script.generation_status === "done"
                        ? "bg-accent-green/10 text-accent-green"
                        : script.generation_status === "generating"
                        ? "bg-accent-yellow/10 text-accent-yellow"
                        : "bg-gray-500/10 text-gray-400"
                    }`}>
                      {script.generation_status}
                    </span>
                  </div>
                </div>
                <span className="text-gray-600 text-xs">
                  {new Date(script.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}