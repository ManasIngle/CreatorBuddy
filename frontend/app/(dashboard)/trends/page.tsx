"use client";
import { useState, useEffect } from "react";
import { trendsApi, channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendRadar, TrendRadarSkeleton, TrendRadarEmpty } from "@/components/intelligence/TrendRadar";
import { TrendingUp, RefreshCw, Clock, Target, AlertCircle } from "lucide-react";
import type { Trend } from "@/types";

const NICHE_OPTIONS = [
  { value: "tech", label: "Tech & Programming" },
  { value: "business", label: "Business & Finance" },
  { value: "lifestyle", label: "Lifestyle & Vlogs" },
  { value: "gaming", label: "Gaming" },
  { value: "education", label: "Education" },
  { value: "entertainment", label: "Entertainment" },
  { value: "sports", label: "Sports & Fitness" },
  { value: "food", label: "Food & Cooking" },
  { value: "travel", label: "Travel" },
  { value: "music", label: "Music" },
];

export default function TrendsPage() {
  const { activeChannel } = useStore();
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedNiche, setSelectedNiche] = useState<string>("");

  useEffect(() => {
    async function loadTrends() {
      try {
        const niche = activeChannel?.niche || selectedNiche;
        const response = await trendsApi.list(niche || undefined);
        setTrends(response.data);
      } catch (e) {
        console.error("Failed to load trends", e);
      } finally {
        setLoading(false);
      }
    }
    loadTrends();
  }, [activeChannel, selectedNiche]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const niche = activeChannel?.niche || selectedNiche;
      const response = await trendsApi.list(niche || undefined);
      setTrends(response.data);
    } catch (e) {
      console.error("Failed to refresh trends", e);
    } finally {
      setRefreshing(false);
    }
  };

  const stats = {
    total: trends.length,
    rising: trends.filter((t) => t.trend_direction === "rising" || t.velocity_score >= 7).length,
    openWindow: trends.filter((t) => t.opportunity_window === "open").length,
    avgVelocity: trends.length > 0
      ? (trends.reduce((sum, t) => sum + t.velocity_score, 0) / trends.length).toFixed(1)
      : 0,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Viral Trend Radar</h1>
          <p className="text-gray-400 text-sm mt-1">
            Track trending topics and opportunity windows in your niche
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select
            value={selectedNiche}
            onChange={(e) => setSelectedNiche(e.target.value)}
            className="w-48"
          >
            <option value="">All Niches</option>
            {NICHE_OPTIONS.map((niche) => (
              <option key={niche.value} value={niche.value}>
                {niche.label}
              </option>
            ))}
          </Select>
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Active Trends", value: stats.total, icon: TrendingUp, color: "text-brand-400" },
          { label: "Rising Fast", value: stats.rising, icon: AlertCircle, color: "text-accent-green" },
          { label: "Open Opportunities", value: stats.openWindow, icon: Target, color: "text-accent-yellow" },
          { label: "Avg Velocity", value: `${stats.avgVelocity}/10`, icon: Clock, color: "text-accent-purple" },
        ].map((stat) => (
          <Card key={stat.label} className="p-4">
            <stat.icon className={`w-5 h-5 ${stat.color} mb-2`} />
            <p className="text-white text-xl font-bold">{stat.value}</p>
            <p className="text-gray-500 text-xs">{stat.label}</p>
          </Card>
        ))}
      </div>

      {/* Trend Radar */}
      {loading ? (
        <TrendRadarSkeleton />
      ) : trends.length === 0 ? (
        <TrendRadarEmpty />
      ) : (
        <TrendRadar trends={trends} />
      )}

      {/* How to Read */}
      <Card className="p-5">
        <h3 className="text-white font-medium mb-3">How to Read Trend Data</h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-accent-green font-medium mb-1">Velocity Score</p>
            <p className="text-gray-400">How fast a trend is growing (0-10). Higher means more momentum.</p>
          </div>
          <div>
            <p className="text-accent-yellow font-medium mb-1">Saturation</p>
            <p className="text-gray-400">How many creators are covering this. Low saturation = more opportunity.</p>
          </div>
          <div>
            <p className="text-accent-blue font-medium mb-1">Opportunity Window</p>
            <p className="text-gray-400">Open (act now), Closing (still viable), Closed (too late).</p>
          </div>
        </div>
      </Card>
    </div>
  );
}