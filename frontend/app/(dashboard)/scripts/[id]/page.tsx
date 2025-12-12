"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { scriptsApi } from "@/lib/api";
import type { Script } from "@/types";
import { Copy, Check } from "lucide-react";

export default function ScriptDetailPage() {
  const { id } = useParams();
  const [script, setScript] = useState<Script | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<"hook" | "full" | "short">("hook");

  useEffect(() => {
    scriptsApi.get(id as string).then((r) => {
      setScript(r.data);
      setLoading(false);
    });
  }, [id]);

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (loading) return <div className="h-64 bg-surface-card rounded-xl animate-pulse" />;
  if (!script) return <p className="text-gray-400">Script not found</p>;

  const TABS = [
    { key: "hook", label: "Hook (30s)", content: script.hook },
    { key: "full", label: "Full Script", content: script.full_script },
    { key: "short", label: "Short-Form", content: script.short_form_adaptation }
  ] as const;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">{script.topic}</h1>
        <p className="text-gray-400 text-sm mt-1">
          {script.format_type} · {script.target_duration_minutes} minutes · Generated {new Date(script.created_at).toLocaleDateString()}
        </p>
      </div>

      {script.title_suggestions.length > 0 && (
        <div className="bg-surface-card border border-surface-border rounded-xl p-5">
          <h3 className="text-white font-semibold text-sm mb-3">Title Suggestions</h3>
          <div className="space-y-2">
            {script.title_suggestions.map((title, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-surface rounded-lg px-3 py-2.5"
              >
                <span className="text-gray-200 text-sm">{title}</span>
                <button
                  onClick={() => copyToClipboard(title)}
                  className="text-gray-500 hover:text-white ml-3 flex-shrink-0"
                >
                  <Copy className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-surface-card border border-surface-border rounded-xl overflow-hidden">
        <div className="flex border-b border-surface-border">
          {TABS.filter(t => t.content).map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-5 py-3 text-sm font-medium transition ${
                activeTab === tab.key
                  ? "text-brand-400 border-b-2 border-brand-500 bg-brand-600/5"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          <div className="flex justify-end mb-3">
            <button
              onClick={() => {
                const content = TABS.find(t => t.key === activeTab)?.content || "";
                copyToClipboard(content);
              }}
              className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm transition"
            >
              {copied ? <Check className="w-4 h-4 text-accent-green" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <pre className="text-gray-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">
            {TABS.find(t => t.key === activeTab)?.content || "Not available"}
          </pre>
        </div>
      </div>

      {script.thumbnail_concept && (
        <div className="bg-surface-card border border-surface-border rounded-xl p-5">
          <h3 className="text-white font-semibold text-sm mb-2">Thumbnail Concept</h3>
          <p className="text-gray-300 text-sm">{script.thumbnail_concept}</p>
        </div>
      )}
    </div>
  );
}