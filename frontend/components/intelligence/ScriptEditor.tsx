"use client";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { Copy, Check, Clock, Play } from "lucide-react";
import type { Script } from "@/types";

interface ScriptEditorProps {
  script: Script;
  className?: string;
}

export function ScriptEditor({ script, className }: ScriptEditorProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const handleCopy = async (text: string, section: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const formatScript = (text: string) => {
    return text
      .replace(/\[PAUSE\]/g, '\n\n⏸️ [PAUSE]\n')
      .replace(/\[EMPHASIS\]/g, '**')
      .replace(/\[B-ROLL:([^\]]+)\]/g, '\n\n🎬 B-ROLL: $1\n')
      .split('\n\n')
      .map((para, i) => (
        <p key={i} className="mb-4 text-gray-300 leading-relaxed whitespace-pre-wrap">
          {para}
        </p>
      ));
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Title Suggestions */}
      {script.title_suggestions && script.title_suggestions.length > 0 && (
        <Card className="p-4">
          <h3 className="text-white font-medium mb-3 flex items-center gap-2">
            <span className="text-accent-yellow">★</span> Title Suggestions
          </h3>
          <div className="space-y-2">
            {script.title_suggestions.map((title, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-2 bg-surface-elevated rounded-lg group"
              >
                <span className="text-gray-300 text-sm">{title}</span>
                <button
                  onClick={() => handleCopy(title, `title-${i}`)}
                  className="opacity-0 group-hover:opacity-100 transition"
                >
                  {copiedSection === `title-${i}` ? (
                    <Check className="w-4 h-4 text-accent-green" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-400" />
                  )}
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Hook */}
      {script.hook && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-medium flex items-center gap-2">
              <span className="text-accent-orange">⚡</span> Opening Hook
            </h3>
            <button
              onClick={() => handleCopy(script.hook!, "hook")}
              className="text-gray-400 hover:text-white transition"
            >
              {copiedSection === "hook" ? (
                <Check className="w-4 h-4 text-accent-green" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed italic border-l-2 border-accent-orange pl-3">
            {script.hook}
          </p>
        </Card>
      )}

      {/* Full Script */}
      {script.full_script && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-medium flex items-center gap-2">
              <span className="text-brand-400">📝</span> Full Script
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(script.full_script!, "script")}
            >
              {copiedSection === "script" ? (
                <Check className="w-4 h-4 mr-1" />
              ) : (
                <Copy className="w-4 h-4 mr-1" />
              )}
              Copy All
            </Button>
          </div>
          <div className="bg-surface-elevated rounded-lg p-4 max-h-96 overflow-y-auto">
            {formatScript(script.full_script)}
          </div>
        </Card>
      )}

      {/* CTA */}
      {script.cta_text && (
        <Card className="p-4">
          <h3 className="text-white font-medium mb-2 flex items-center gap-2">
            <span className="text-accent-green">👉</span> Call to Action
          </h3>
          <p className="text-gray-300 text-sm">{script.cta_text}</p>
        </Card>
      )}

      {/* Short Form Adaptation */}
      {script.short_form_adaptation && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-medium flex items-center gap-2">
              <Play className="w-4 h-4 text-accent-red" />
              Short Form (60s)
            </h3>
            <button
              onClick={() => handleCopy(script.short_form_adaptation!, "short")}
              className="text-gray-400 hover:text-white transition"
            >
              {copiedSection === "short" ? (
                <Check className="w-4 h-4 text-accent-green" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
          <p className="text-gray-300 text-sm">{script.short_form_adaptation}</p>
        </Card>
      )}

      {/* Thumbnail Concept */}
      {script.thumbnail_concept && (
        <Card className="p-4">
          <h3 className="text-white font-medium mb-2 flex items-center gap-2">
            <span className="text-accent-purple">🖼️</span> Thumbnail Concept
          </h3>
          <p className="text-gray-300 text-sm">{script.thumbnail_concept}</p>
        </Card>
      )}

      {/* Meta Info */}
      <div className="flex items-center gap-4 text-gray-500 text-xs">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          ~{script.target_duration_minutes} min
        </span>
        <span>Format: {script.format_type}</span>
      </div>
    </div>
  );
}

export function ScriptEditorSkeleton() {
  return (
    <div className="space-y-4">
      <Card className="p-4">
        <Skeleton className="h-5 w-32 mb-3" />
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </Card>
      <Card className="p-4">
        <Skeleton className="h-5 w-24 mb-3" />
        <Skeleton className="h-20 w-full" />
      </Card>
      <Card className="p-4">
        <Skeleton className="h-5 w-32 mb-3" />
        <Skeleton className="h-40 w-full" />
      </Card>
    </div>
  );
}

export function ScriptEditorEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <p className="text-gray-400 text-sm text-center">No script content available</p>
    </Card>
  );
}