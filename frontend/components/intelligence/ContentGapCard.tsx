"use client";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendingUp, TrendingDown, Minus, Lightbulb, Target, Zap } from "lucide-react";
import type { ContentGap } from "@/types";

interface ContentGapCardProps {
  gap: ContentGap;
  className?: string;
}

export function ContentGapCard({ gap, className }: ContentGapCardProps) {
  const trendIcon = gap.trend_direction === "rising"
    ? TrendingUp
    : gap.trend_direction === "declining"
    ? TrendingDown
    : Minus;

  const trendColor = gap.trend_direction === "rising"
    ? "text-accent-green"
    : gap.trend_direction === "declining"
    ? "text-accent-red"
    : "text-gray-400";

  const scoreColor = gap.opportunity_score >= 7
    ? "text-accent-green"
    : gap.opportunity_score >= 5
    ? "text-accent-yellow"
    : "text-accent-orange";

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-brand-400" />
          <h3 className="text-white font-medium">{gap.topic}</h3>
        </div>
        <div className="flex items-center gap-2">
          <trendIcon className={`w-4 h-4 ${trendColor}`} />
          <Badge
            variant={
              gap.competition_level === "low"
                ? "green"
                : gap.competition_level === "medium"
                ? "yellow"
                : "orange"
            }
          >
            {gap.competition_level}
          </Badge>
        </div>
      </div>

      <p className="text-gray-400 text-sm mb-3">{gap.reason}</p>

      {gap.suggested_angle && (
        <div className="flex items-start gap-2 p-2 bg-surface-elevated rounded-lg mb-3">
          <Lightbulb className="w-4 h-4 text-accent-yellow flex-shrink-0 mt-0.5" />
          <p className="text-gray-300 text-xs">{gap.suggested_angle}</p>
        </div>
      )}

      <div className="flex items-center justify-between pt-3 border-t border-surface-border">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-brand-400" />
          <span className={`font-semibold text-sm ${scoreColor}`}>
            {gap.opportunity_score.toFixed(1)}/10
          </span>
          <span className="text-gray-500 text-xs">opportunity score</span>
        </div>
        {gap.suggested_title && (
          <Badge variant="subtle" className="text-xs">
            Title ready
          </Badge>
        )}
      </div>
    </Card>
  );
}

export function ContentGapCardSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-3/4 mb-3" />
      <Skeleton className="h-12 w-full mb-3" />
      <div className="flex items-center justify-between pt-3 border-t border-surface-border">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-16" />
      </div>
    </Card>
  );
}

export function ContentGapCardEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <Target className="w-10 h-10 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No content gaps detected</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Run gap detection to discover opportunities
      </p>
    </Card>
  );
}