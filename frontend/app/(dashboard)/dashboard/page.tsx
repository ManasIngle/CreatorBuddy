"use client";
import { useEffect, useState } from "react";
import { channelsApi, gapsApi, trendsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import type { Channel, ContentGap, Trend } from "@/types";
import Link from "next/link";
import { TrendingUp, Search, Zap, FileText, ArrowRight, AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const { activeChannel, setActiveChannel } = useStore();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [gaps, setGaps] = useState<ContentGap[]>([]);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const chResp = await channelsApi.list();
        setChannels(chResp.data);
        if (chResp.data.length > 0 && !activeChannel) {
          setActiveChannel(chResp.data[0]);
        }
        if (chResp.data.length > 0) {
          const [gapResp, trendResp] = await Promise.all([
            gapsApi.list(chResp.data[0].id),
            trendsApi.list(chResp.data[0].niche || undefined)
          ]);
          setGaps(gapResp.data.slice(0, 3));
          setTrends(trendResp.data.slice(0, 3));
        }
      } catch (e) {
        // handle error
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-32 bg-surface-card rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (channels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center py-20">
        <div className="w-16 h-16 rounded-full bg-brand-600/20 flex items-center justify-center mb-4">
          <AlertCircle className="w-8 h-8 text-brand-400" />
        </div>
        <h2 className="text-xl font-semibold text-white mb-2">Connect your channel</h2>
        <p className="text-gray-400 mb-6 max-w-sm">
          Connect your YouTube channel to start getting AI-powered growth intelligence.
        </p>
        <Link
          href="/channel"
          className="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2.5 rounded-lg font-medium transition"
        >
          Connect YouTube Channel
        </Link>
      </div>
    );
  }

  const channel = channels[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Growth Overview</h1>
        <p className="text-gray-400 text-sm mt-1">
          {channel.analysis_status === "done"
            ? `AI analysis complete for ${channel.title}`
            : channel.analysis_status === "running"
            ? "Analyzing your channel... this takes 2-3 minutes"
            : "Connect your channel and start analyzing"}
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Subscribers", value: channel.subscriber_count.toLocaleString(), color: "brand" },
          { label: "Avg Views", value: Math.round(channel.avg_views).toLocaleString(), color: "green" },
          { label: "Content Gaps", value: gaps.length.toString(), color: "orange" },
          { label: "Niche", value: channel.niche || "Detecting...", color: "purple" }
        ].map((stat) => (
          <div key={stat.label} className="bg-surface-card border border-surface-border rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-1">{stat.label}</p>
            <p className="text-white text-xl font-bold truncate">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-surface-card border border-surface-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-accent-orange" />
              <h3 className="font-semibold text-white text-sm">Top Content Gaps</h3>
            </div>
            <Link href="/gaps" className="text-brand-400 text-xs flex items-center gap-1 hover:gap-2 transition-all">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {gaps.length === 0 ? (
            <p className="text-gray-500 text-sm">
              No gaps detected yet.{" "}
              <button
                onClick={() => gapsApi.detect(channel.id)}
                className="text-brand-400 underline"
              >
                Detect gaps
              </button>
            </p>
          ) : (
            <div className="space-y-3">
              {gaps.map((gap) => (
                <div key={gap.id} className="flex items-start gap-3">
                  <div className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                    gap.opportunity_score >= 7 ? "bg-accent-green" :
                    gap.opportunity_score >= 5 ? "bg-accent-yellow" : "bg-accent-orange"
                  }`} />
                  <div>
                    <p className="text-white text-sm font-medium">{gap.topic}</p>
                    <p className="text-gray-500 text-xs">{gap.competition_level} competition · {gap.trend_direction}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-surface-card border border-surface-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-accent-green" />
              <h3 className="font-semibold text-white text-sm">Trending in Your Niche</h3>
            </div>
            <Link href="/trends" className="text-brand-400 text-xs flex items-center gap-1 hover:gap-2 transition-all">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {trends.length === 0 ? (
            <p className="text-gray-500 text-sm">No trend data available yet.</p>
          ) : (
            <div className="space-y-3">
              {trends.map((trend) => (
                <div key={trend.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-white text-sm font-medium">{trend.topic}</p>
                    <p className="text-gray-500 text-xs">Velocity: {trend.velocity_score.toFixed(1)}/10</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    trend.opportunity_window === "open"
                      ? "bg-accent-green/10 text-accent-green"
                      : trend.opportunity_window === "closing"
                      ? "bg-accent-yellow/10 text-accent-yellow"
                      : "bg-gray-500/10 text-gray-400"
                  }`}>
                    {trend.opportunity_window}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Generate Script", desc: "AI-powered script for your next video", href: "/scripts/new", icon: FileText, color: "brand" },
          { label: "Analyze Competitors", desc: "See what's working for others", href: "/competitors", icon: TrendingUp, color: "purple" },
          { label: "Generate Hooks", desc: "Get viral hook suggestions", href: "/hooks", icon: Zap, color: "orange" }
        ].map((action) => (
          <Link
            key={action.label}
            href={action.href}
            className="bg-surface-card border border-surface-border rounded-xl p-4 hover:border-brand-600/50 transition group"
          >
            <div className="flex items-center gap-3 mb-2">
              <action.icon className="w-5 h-5 text-brand-400" />
              <span className="text-white font-medium text-sm">{action.label}</span>
            </div>
            <p className="text-gray-500 text-xs">{action.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}