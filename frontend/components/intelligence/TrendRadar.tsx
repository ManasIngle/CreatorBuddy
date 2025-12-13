"use client";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { TrendChart, TrendVelocityBar } from "@/components/charts/TrendChart";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendingUp, Clock, Target, AlertCircle, CheckCircle2 } from "lucide-react";
import type { Trend } from "@/types";

interface TrendRadarProps {
  trends: Trend[];
  className?: string;
}

export function TrendRadar({ trends, className }: TrendRadarProps) {
  const [selectedTrend, setSelectedTrend] = useState<Trend | null>(null);

  const chartData = trends.map((t) => ({
    topic: t.topic.length > 15 ? t.topic.substring(0, 15) + "..." : t.topic,
    velocity: t.velocity_score,
    saturation: t.saturation_score,
    opportunity: 10 - t.saturation_score + t.velocity_score / 2,
  }));

  const windowColors = {
    open: "bg-accent-green/10 text-accent-green border-accent-green/30",
    closing: "bg-accent-yellow/10 text-accent-yellow border-accent-yellow/30",
    closed: "bg-gray-500/10 text-gray-400 border-gray-500/30",
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Radar Chart */}
      {chartData.length > 0 && (
        <Card className="p-4">
          <h3 className="text-white font-medium mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-brand-400" />
            Trend Velocity & Saturation
          </h3>
          <TrendChart data={chartData} />
        </Card>
      )}

      {/* Trend List */}
      <div className="space-y-2">
        {trends.map((trend) => (
          <Card
            key={trend.id}
            className={`p-3 cursor-pointer transition ${
              selectedTrend?.id === trend.id
                ? "border-brand-600 bg-surface-elevated"
                : "hover:border-brand-600/30"
            }`}
            onClick={() => setSelectedTrend(selectedTrend?.id === trend.id ? null : trend)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div>
                  <h4 className="text-white text-sm font-medium">{trend.topic}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <TrendVelocityBar velocity={trend.velocity_score} />
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant={
                    trend.opportunity_window === "open"
                      ? "green"
                      : trend.opportunity_window === "closing"
                      ? "yellow"
                      : "subtle"
                  }
                  className="text-xs"
                >
                  {trend.opportunity_window === "open" && (
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                  )}
                  {trend.opportunity_window}
                </Badge>
              </div>
            </div>

            {selectedTrend?.id === trend.id && (
              <div className="mt-3 pt-3 border-t border-surface-border space-y-2">
                {trend.recommended_action && (
                  <div className="flex items-start gap-2">
                    <Target className="w-4 h-4 text-accent-orange flex-shrink-0 mt-0.5" />
                    <p className="text-gray-300 text-xs">{trend.recommended_action}</p>
                  </div>
                )}
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Detected {new Date(trend.first_detected_at).toLocaleDateString()}
                  </span>
                  <span>Saturation: {trend.saturation_score.toFixed(1)}/10</span>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {trends.length === 0 && (
        <Card className="p-8 flex flex-col items-center justify-center">
          <AlertCircle className="w-10 h-10 text-gray-600 mb-3" />
          <p className="text-gray-400 text-sm text-center">No trends detected</p>
          <p className="text-gray-500 text-xs text-center mt-1">
            Trends are refreshed daily
          </p>
        </Card>
      )}
    </div>
  );
}

export function TrendRadarSkeleton() {
  return (
    <div className="space-y-4">
      <Card className="p-4">
        <Skeleton className="h-6 w-40 mb-4" />
        <Skeleton className="h-64 w-full" />
      </Card>
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-5 w-32 mb-2" />
              <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className="h-6 w-16" />
          </div>
        </Card>
      ))}
    </div>
  );
}

export function TrendRadarEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <TrendingUp className="w-10 h-10 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No trend data available</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Set your niche to see trending topics
      </p>
    </Card>
  );
}