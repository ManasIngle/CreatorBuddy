"use client";
import { useState, useEffect } from "react";
import { gapsApi, channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ContentGapCard, ContentGapCardSkeleton, ContentGapCardEmpty } from "@/components/intelligence/ContentGapCard";
import { Search, Target, TrendingUp, RefreshCw, Filter, AlertCircle } from "lucide-react";
import type { ContentGap, Channel } from "@/types";

export default function GapsPage() {
  const { activeChannel } = useStore();
  const [gaps, setGaps] = useState<ContentGap[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [filter, setFilter] = useState<"all" | "low" | "medium" | "high">("all");
  const [sortBy, setSortBy] = useState<"score" | "trend">("score");

  useEffect(() => {
    async function loadGaps() {
      if (!activeChannel) {
        setLoading(false);
        return;
      }
      try {
        const response = await gapsApi.list(activeChannel.id);
        setGaps(response.data);
      } catch (e) {
        console.error("Failed to load gaps", e);
      } finally {
        setLoading(false);
      }
    }
    loadGaps();
  }, [activeChannel]);

  const handleDetectGaps = async () => {
    if (!activeChannel) return;
    setDetecting(true);
    try {
      await gapsApi.detect(activeChannel.id);
      const response = await gapsApi.list(activeChannel.id);
      setGaps(response.data);
    } catch (e) {
      console.error("Failed to detect gaps", e);
    } finally {
      setDetecting(false);
    }
  };

  const filteredGaps = gaps
    .filter((gap) => filter === "all" || gap.competition_level === filter)
    .sort((a, b) => {
      if (sortBy === "score") return b.opportunity_score - a.opportunity_score;
      const trendOrder = { rising: 0, stable: 1, declining: 2 };
      return trendOrder[a.trend_direction] - trendOrder[b.trend_direction];
    });

  const stats = {
    total: gaps.length,
    highOpportunity: gaps.filter((g) => g.opportunity_score >= 7).length,
    rising: gaps.filter((g) => g.trend_direction === "rising").length,
    lowCompetition: gaps.filter((g) => g.competition_level === "low").length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Gap Detection</h1>
          <p className="text-gray-400 text-sm mt-1">
            Discover untapped opportunities in your niche
          </p>
        </div>
        <Button
          onClick={handleDetectGaps}
          disabled={!activeChannel || detecting}
          className="flex items-center gap-2"
        >
          {detecting ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          {detecting ? "Detecting..." : "Detect Gaps"}
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Gaps", value: stats.total, icon: Target, color: "text-brand-400" },
          { label: "High Opportunity", value: stats.highOpportunity, icon: TrendingUp, color: "text-accent-green" },
          { label: "Rising Trends", value: stats.rising, icon: AlertCircle, color: "text-accent-yellow" },
          { label: "Low Competition", value: stats.lowCompetition, icon: Filter, color: "text-accent-purple" },
        ].map((stat) => (
          <Card key={stat.label} className="p-4">
            <div className="flex items-center gap-3">
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
              <div>
                <p className="text-white text-xl font-bold">{stat.value}</p>
                <p className="text-gray-500 text-xs">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">Competition:</span>
          {(["all", "low", "medium", "high"] as const).map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                filter === level
                  ? "bg-brand-600 text-white"
                  : "bg-surface-card text-gray-400 hover:text-white"
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "score" | "trend")}
            className="bg-surface-card border border-surface-border rounded-lg px-3 py-1.5 text-xs text-white"
          >
            <option value="score">Opportunity Score</option>
            <option value="trend">Trend Direction</option>
          </select>
        </div>
      </div>

      {/* Gap List */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <ContentGapCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredGaps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Target className="w-12 h-12 text-gray-600 mb-4" />
          {gaps.length === 0 ? (
            <>
              <p className="text-gray-400 text-center">No content gaps detected yet</p>
              <p className="text-gray-500 text-sm text-center mt-1">
                Click "Detect Gaps" to analyze opportunities
              </p>
            </>
          ) : (
            <>
              <p className="text-gray-400 text-center">No gaps match your filter</p>
              <Button variant="ghost" size="sm" onClick={() => setFilter("all")}>
                Clear Filter
              </Button>
            </>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {filteredGaps.map((gap) => (
            <ContentGapCard key={gap.id} gap={gap} />
          ))}
        </div>
      )}
    </div>
  );
}