"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { scriptsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Sparkles, Clock } from "lucide-react";

const FORMAT_TYPES = [
  { value: "educational", label: "Educational / Tutorial" },
  { value: "story", label: "Story-Driven" },
  { value: "list", label: "Listicle / Countdown" },
  { value: "review", label: "Review / Opinion" },
  { value: "commentary", label: "Commentary / Analysis" }
];

const DURATIONS = [5, 8, 10, 15, 20];

export default function NewScriptPage() {
  const router = useRouter();
  const { activeChannel } = useStore();
  const [topic, setTopic] = useState("");
  const [formatType, setFormatType] = useState("educational");
  const [duration, setDuration] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!topic.trim()) return;
    setLoading(true);
    setError("");
    try {
      const resp = await scriptsApi.generate({
        topic,
        channel_id: activeChannel?.id,
        target_duration_minutes: duration,
        format_type: formatType
      });
      router.push(`/scripts/${resp.data.id}`);
    } catch (e: any) {
      setError("Script generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Generate Script</h1>
        <p className="text-gray-400 text-sm">
          {activeChannel
            ? `Personalized for ${activeChannel.title}'s style and audience`
            : "Connect a channel for personalized scripts"}
        </p>
      </div>

      <div className="bg-surface-card border border-surface-border rounded-2xl p-6 space-y-6">
        <div>
          <label className="text-sm font-medium text-gray-300 block mb-2">
            What is this video about?
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            rows={3}
            className="w-full bg-surface border border-surface-border rounded-lg px-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500 transition resize-none"
            placeholder="e.g., 'How to grow a YouTube channel from 0 to 10,000 subscribers'"
          />
          <p className="text-gray-600 text-xs mt-1">Be specific. The more detail, the better the script.</p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-300 block mb-2">Video Format</label>
          <div className="grid grid-cols-2 gap-2">
            {FORMAT_TYPES.map((fmt) => (
              <button
                key={fmt.value}
                onClick={() => setFormatType(fmt.value)}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium border transition text-left ${
                  formatType === fmt.value
                    ? "bg-brand-600/20 border-brand-600/50 text-brand-400"
                    : "border-surface-border text-gray-400 hover:border-gray-500"
                }`}
              >
                {fmt.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-300 block mb-2">
            <Clock className="w-4 h-4 inline mr-1.5 mb-0.5" />
            Target Duration
          </label>
          <div className="flex gap-2">
            {DURATIONS.map((d) => (
              <button
                key={d}
                onClick={() => setDuration(d)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium border transition ${
                  duration === d
                    ? "bg-brand-600/20 border-brand-600/50 text-brand-400"
                    : "border-surface-border text-gray-400 hover:border-gray-500"
                }`}
              >
                {d} min
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleGenerate}
          disabled={loading || !topic.trim()}
          className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Generating... (15-30 seconds)
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Script
            </>
          )}
        </button>

        <p className="text-gray-600 text-xs text-center">
          Script generation uses your channel's personality, speaking style, and audience data.
        </p>
      </div>
    </div>
  );
}