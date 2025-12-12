"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { competitorsApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { RetentionChart, RetentionSkeleton } from "@/components/charts/RetentionChart";
import {
  TrendingUp, Users, Eye, Zap, Brain, Image, Clock, ArrowLeft,
  Lightbulb, MessageSquare, Target, RefreshCw
} from "lucide-react";
import Link from "next/link";
import type { Competitor } from "@/types";

export default function CompetitorDetailPage() {
  const params = useParams();
  const competitorId = params.id as string;
  const channelId = "default-channel"; // In real app, get from context/router

  const [competitor, setCompetitor] = useState<Competitor | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    async function loadCompetitor() {
      try {
        const response = await competitorsApi.get(channelId, competitorId);
        setCompetitor(response.data);
      } catch (e) {
        console.error("Failed to load competitor", e);
      } finally {
        setLoading(false);
      }
    }
    loadCompetitor();
  }, [channelId, competitorId]);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card className="p-6">
          <div className="flex items-start gap-4 mb-6">
            <Skeleton className="w-20 h-20 rounded-full" />
            <div className="flex-1">
              <Skeleton className="h-6 w-40 mb-2" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
          <Skeleton className="h-64 w-full" />
        </Card>
      </div>
    );
  }

  if (!competitor) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <p className="text-gray-400">Competitor not found</p>
        <Link href="/competitors" className="text-brand-400 text-sm mt-2">
          Back to competitors
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/competitors" className="text-gray-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <Avatar src={competitor.thumbnail_url} alt={competitor.title} size="xl" />
          <div>
            <h1 className="text-2xl font-bold text-white">{competitor.title}</h1>
            <div className="flex items-center gap-3 mt-1">
              <Badge variant={competitor.analysis_status === "done" ? "green" : "yellow"}>
                {competitor.analysis_status}
              </Badge>
              <span className="text-gray-400 text-sm flex items-center gap-1">
                <Users className="w-3 h-3" />
                {competitor.subscriber_count.toLocaleString()} subs
              </span>
            </div>
          </div>
        </div>
        <Button variant="ghost" className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Re-analyze
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Avg Views", value: Math.round(competitor.avg_views).toLocaleString(), icon: Eye, color: "text-accent-blue" },
          { label: "Overlap", value: `${(competitor.niche_overlap_score * 100).toFixed(0)}%`, icon: TrendingUp, color: "text-accent-green" },
          { label: "Formats", value: competitor.best_formats?.length || 0, icon: Zap, color: "text-accent-orange" },
          { label: "Hooks", value: competitor.hook_patterns?.length || 0, icon: MessageSquare, color: "text-accent-purple" },
        ].map((stat) => (
          <Card key={stat.label} className="p-4">
            <stat.icon className={`w-4 h-4 ${stat.color} mb-2`} />
            <p className="text-white text-xl font-bold">{stat.value}</p>
            <p className="text-gray-500 text-xs">{stat.label}</p>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { id: "overview", label: "AI Analysis" },
          { id: "hooks", label: "Hook Patterns" },
          { id: "content", label: "Content Gaps" },
        ]}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-2 gap-6">
          {/* Why They Succeed */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-semibold">Why They Succeed</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              {competitor.why_they_succeed || "Analysis pending..."}
            </p>
          </Card>

          {/* Thumbnail Style */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Image className="w-4 h-4 text-accent-purple" />
              <h3 className="text-white font-semibold">Thumbnail Style</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              {competitor.thumbnail_style || "Analysis pending..."}
            </p>
          </Card>

          {/* Emotional Triggers */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-accent-yellow" />
              <h3 className="text-white font-semibold">Emotional Triggers</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {competitor.emotional_triggers_used?.map((trigger) => (
                <Badge key={trigger} variant="orange">{trigger}</Badge>
              )) || <span className="text-gray-500 text-sm">Analysis pending...</span>}
            </div>
          </Card>

          {/* Best Formats */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-4 h-4 text-accent-green" />
              <h3 className="text-white font-semibold">Best Content Formats</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {competitor.best_formats?.map((format) => (
                <Badge key={format} variant="green">{format}</Badge>
              )) || <span className="text-gray-500 text-sm">Analysis pending...</span>}
            </div>
          </Card>
        </div>
      )}

      {activeTab === "hooks" && (
        <Card className="p-5">
          <h3 className="text-white font-semibold mb-4">Hook Patterns</h3>
          {competitor.hook_patterns && competitor.hook_patterns.length > 0 ? (
            <div className="space-y-3">
              {competitor.hook_patterns.map((pattern, i) => (
                <div key={i} className="p-3 bg-surface-elevated rounded-lg">
                  <p className="text-gray-300 text-sm">{pattern}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Hook analysis pending...</p>
          )}
        </Card>
      )}

      {activeTab === "content" && (
        <Card className="p-5">
          <h3 className="text-white font-semibold mb-4">Content Gaps</h3>
          {competitor.content_gaps && competitor.content_gaps.length > 0 ? (
            <div className="space-y-2">
              {competitor.content_gaps.map((gap, i) => (
                <div key={i} className="flex items-start gap-2 p-3 bg-surface-elevated rounded-lg">
                  <Lightbulb className="w-4 h-4 text-accent-yellow flex-shrink-0 mt-0.5" />
                  <p className="text-gray-300 text-sm">{gap}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Content gap analysis pending...</p>
          )}
        </Card>
      )}
    </div>
  );
}