"use client";
import { useState, useEffect } from "react";
import { hooksApi, channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { HookCard, HookCardSkeleton, HookCardEmpty } from "@/components/intelligence/HookCard";
import { Plus, Zap, Filter, Sparkles, AlertTriangle, MessageCircle, HelpCircle, Crossroads } from "lucide-react";
import type { Hook } from "@/types";

const HOOK_TYPES = [
  { id: "all", label: "All", icon: Filter },
  { id: "curiosity", label: "Curiosity", icon: Sparkles },
  { id: "shock", label: "Shock", icon: AlertTriangle },
  { id: "story", label: "Story", icon: MessageCircle },
  { id: "question", label: "Question", icon: HelpCircle },
  { id: "contrarian", label: "Contrarian", icon: Crossroads },
];

export default function HooksPage() {
  const { activeChannel } = useStore();
  const [hooks, setHooks] = useState<Hook[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [topic, setTopic] = useState("");
  const [generating, setGenerating] = useState(false);
  const [selectedHook, setSelectedHook] = useState<Hook | null>(null);
  const [generateError, setGenerateError] = useState("");

  const handleOpenGenerateModal = () => {
    setGenerateError("");
    setTopic("");
    setShowGenerateModal(true);
  };

  useEffect(() => {
    async function loadHooks() {
      try {
        const response = await hooksApi.list(activeChannel?.id);
        setHooks(response.data);
      } catch (e) {
        console.error("Failed to load hooks", e);
      } finally {
        setLoading(false);
      }
    }
    loadHooks();
  }, [activeChannel]);

  const handleGenerateHooks = async () => {
    if (!activeChannel || !topic.trim()) return;
    setGenerating(true);
    setGenerateError("");
    try {
      await hooksApi.generate(activeChannel.id, topic.trim());
      const response = await hooksApi.list(activeChannel.id);
      setHooks(response.data);
      setShowGenerateModal(false);
      setTopic("");
    } catch (e: any) {
      console.error("Failed to generate hooks", e);
      setGenerateError(e.response?.data?.detail || "Failed to generate hooks. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  const filteredHooks = hooks.filter(
    (hook) => filter === "all" || hook.hook_type === filter
  );

  const stats = {
    total: hooks.length,
    byType: Object.fromEntries(
      HOOK_TYPES.slice(1).map(({ id }) => [
        id,
        hooks.filter((h) => h.hook_type === id).length,
      ])
    ),
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Hook Intelligence</h1>
          <p className="text-gray-400 text-sm mt-1">
            AI-generated viral hooks for your content
          </p>
        </div>
        <Button
          onClick={handleOpenGenerateModal}
          disabled={!activeChannel}
          className="flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          Generate Hooks
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-4">
        {HOOK_TYPES.slice(1).map(({ id, label, icon: Icon }) => (
          <Card
            key={id}
            className={`p-3 cursor-pointer transition ${
              filter === id ? "border-brand-600" : "hover:border-brand-600/30"
            }`}
            onClick={() => setFilter(filter === id ? "all" : id)}
          >
            <Icon className={`w-4 h-4 mb-1 ${filter === id ? "text-brand-400" : "text-gray-500"}`} />
            <p className="text-white text-lg font-bold">{stats.byType[id] || 0}</p>
            <p className="text-gray-500 text-xs">{label}</p>
          </Card>
        ))}
      </div>

      {/* Hook List */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <HookCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredHooks.length === 0 ? (
        <HookCardEmpty />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filteredHooks.map((hook) => (
            <HookCard
              key={hook.id}
              hook={hook}
              onClick={() => setSelectedHook(hook)}
            />
          ))}
        </div>
      )}

      {/* Hook Detail Modal */}
      <Modal
        isOpen={!!selectedHook}
        onClose={() => setSelectedHook(null)}
        title="Hook Details"
      >
        {selectedHook && (
          <div className="space-y-4">
            <div className="p-4 bg-surface-elevated rounded-lg">
              <p className="text-gray-200 text-sm leading-relaxed">{selectedHook.hook_text}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="text-gray-400 text-sm">
                Type: <span className="text-white capitalize">{selectedHook.hook_type.replace("_", " ")}</span>
              </span>
              {selectedHook.emotional_trigger && (
                <span className="text-gray-400 text-sm">
                  Trigger: <span className="text-white">{selectedHook.emotional_trigger}</span>
                </span>
              )}
              {selectedHook.predicted_retention_boost && (
                <span className="text-gray-400 text-sm">
                  Retention Boost: <span className="text-accent-green">+{selectedHook.predicted_retention_boost.toFixed(0)}%</span>
                </span>
              )}
            </div>
            <div className="flex justify-end">
              <Button
                variant="ghost"
                onClick={async () => {
                  await navigator.clipboard.writeText(selectedHook.hook_text);
                }}
              >
                Copy to Clipboard
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Generate Modal */}
      <Modal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        title="Generate Hooks"
      >
        <div className="space-y-4">
          <div>
            <label className="text-white text-sm font-medium block mb-2">
              Video Topic
            </label>
            <Input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter your video topic..."
            />
          </div>
          {generateError && (
            <div className="bg-accent-red/10 border border-accent-red/20 rounded-lg p-3 text-accent-red text-xs">
              {generateError}
            </div>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" onClick={() => setShowGenerateModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleGenerateHooks}
              disabled={generating || !topic.trim()}
              className="flex items-center gap-2"
            >
              {generating && <Zap className="w-4 h-4 animate-spin" />}
              {generating ? "Generating..." : "Generate"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}