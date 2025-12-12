"use client";
import { useEffect, useState } from "react";
import { channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import type { Channel } from "@/types";
import { Youtube, Users, TrendingUp, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react";

export default function ChannelPage() {
  const { activeChannel, setActiveChannel } = useStore();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [channelIdInput, setChannelIdInput] = useState("");

  useEffect(() => {
    channelsApi.list().then((r) => {
      setChannels(r.data);
      if (r.data.length > 0 && !activeChannel) {
        setActiveChannel(r.data[0]);
      }
      setLoading(false);
    });
  }, []);

  async function handleConnect() {
    if (!channelIdInput.trim()) return;
    setConnecting(true);
    try {
      const resp = await channelsApi.connect(channelIdInput);
      setChannels([...channels, resp.data]);
      setActiveChannel(resp.data);
      setChannelIdInput("");
    } catch (e) {
      console.error("Failed to connect channel:", e);
    } finally {
      setConnecting(false);
    }
  }

  async function handleReanalyze(channel: Channel) {
    await channelsApi.reanalyze(channel.id);
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-surface-card rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">My Channel</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your connected YouTube channels</p>
      </div>

      {channels.length === 0 ? (
        <div className="bg-surface-card border border-surface-border rounded-2xl p-8 text-center">
          <Youtube className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Connect your YouTube channel</h2>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Enter your YouTube channel ID or handle to connect and start receiving AI-powered insights.
          </p>
          <div className="flex gap-3 max-w-md mx-auto">
            <input
              type="text"
              value={channelIdInput}
              onChange={(e) => setChannelIdInput(e.target.value)}
              placeholder="UC... or @username"
              className="flex-1 bg-surface border border-surface-border rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500"
            />
            <button
              onClick={handleConnect}
              disabled={connecting || !channelIdInput.trim()}
              className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium px-5 py-2.5 rounded-lg transition"
            >
              {connecting ? "Connecting..." : "Connect"}
            </button>
          </div>
          <p className="text-gray-600 text-xs mt-3">Your channel ID starts with UC and is found in your channel URL</p>
        </div>
      ) : (
        <div className="space-y-4">
          {channels.map((channel) => (
            <div key={channel.id} className="bg-surface-card border border-surface-border rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  {channel.thumbnail_url && (
                    <img src={channel.thumbnail_url} alt={channel.title} className="w-16 h-16 rounded-full" />
                  )}
                  <div>
                    <h3 className="text-white font-semibold text-lg">{channel.title}</h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
                      <span>{channel.subscriber_count.toLocaleString()} subscribers</span>
                      <span>{channel.video_count} videos</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    channel.analysis_status === "done"
                      ? "bg-accent-green/10 text-accent-green"
                      : channel.analysis_status === "running"
                      ? "bg-accent-yellow/10 text-accent-yellow"
                      : "bg-gray-500/10 text-gray-400"
                  }`}>
                    {channel.analysis_status === "done" ? (
                      <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Analyzed</span>
                    ) : channel.analysis_status === "running" ? (
                      <span className="flex items-center gap-1"><RefreshCw className="w-3 h-3 animate-spin" /> Analyzing</span>
                    ) : (
                      <span className="flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Pending</span>
                    )}
                  </span>
                  {channel.analysis_status !== "running" && (
                    <button
                      onClick={() => handleReanalyze(channel)}
                      className="p-2 text-gray-400 hover:text-white transition"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {channel.analysis_status === "done" && (
                <div className="grid grid-cols-4 gap-4 mt-5 pt-5 border-t border-surface-border">
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Niche</p>
                    <p className="text-white text-sm font-medium">{channel.niche || "Not detected"}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Avg Views</p>
                    <p className="text-white text-sm font-medium">{Math.round(channel.avg_views).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Engagement</p>
                    <p className="text-white text-sm font-medium">{(channel.avg_engagement_rate * 100).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Audience</p>
                    <p className="text-white text-sm font-medium truncate">{channel.audience_type || "Not detected"}</p>
                  </div>
                </div>
              )}

              {channel.niche_tags && channel.niche_tags.length > 0 && (
                <div className="flex gap-2 mt-4 flex-wrap">
                  {channel.niche_tags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-brand-600/10 text-brand-400 border border-brand-600/20">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          <div className="border border-dashed border-surface-border rounded-xl p-5 text-center">
            <p className="text-gray-400 text-sm mb-3">Add another channel</p>
            <div className="flex gap-3 max-w-md mx-auto">
              <input
                type="text"
                value={channelIdInput}
                onChange={(e) => setChannelIdInput(e.target.value)}
                placeholder="UC... or @username"
                className="flex-1 bg-surface border border-surface-border rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-brand-500"
              />
              <button
                onClick={handleConnect}
                disabled={connecting || !channelIdInput.trim()}
                className="bg-surface hover:bg-surface-border text-white font-medium px-5 py-2.5 rounded-lg transition disabled:opacity-50"
              >
                {connecting ? "Connecting..." : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}