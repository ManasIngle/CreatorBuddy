"use client";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendingUp, Eye, Users, ArrowRight } from "lucide-react";
import Link from "next/link";
import type { Competitor } from "@/types";

interface CompetitorCardProps {
  competitor: Competitor;
  channelId: string;
  className?: string;
}

export function CompetitorCard({ competitor, channelId, className }: CompetitorCardProps) {
  const overlapColor = competitor.niche_overlap_score >= 0.7
    ? "accent-green"
    : competitor.niche_overlap_score >= 0.4
    ? "accent-yellow"
    : "accent-orange";

  return (
    <Card className={`p-4 hover:border-brand-600/50 transition group ${className}`}>
      <div className="flex items-start gap-3">
        <Avatar
          src={competitor.thumbnail_url}
          alt={competitor.title}
          size="lg"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h3 className="text-white font-medium truncate">{competitor.title}</h3>
            <Badge variant={overlapColor as "green" | "yellow" | "orange"}>
              {Math.round(competitor.niche_overlap_score * 100)}% overlap
            </Badge>
          </div>

          <div className="flex items-center gap-4 mt-2 text-sm">
            <span className="flex items-center gap-1 text-gray-400">
              <Users className="w-3 h-3" />
              {competitor.subscriber_count.toLocaleString()}
            </span>
            <span className="flex items-center gap-1 text-gray-400">
              <Eye className="w-3 h-3" />
              {Math.round(competitor.avg_views).toLocaleString()} avg views
            </span>
          </div>

          {competitor.why_they_succeed && (
            <p className="text-gray-400 text-xs mt-2 line-clamp-2">
              {competitor.why_they_succeed}
            </p>
          )}

          <div className="flex flex-wrap gap-1.5 mt-2">
            {competitor.best_formats?.slice(0, 3).map((format) => (
              <Badge key={format} variant="subtle" className="text-xs">
                {format}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <Link
        href={`/competitors/${competitor.id}`}
        className="flex items-center justify-center gap-1 mt-3 text-brand-400 text-sm hover:text-brand-300 transition"
      >
        View Analysis <ArrowRight className="w-3 h-3" />
      </Link>
    </Card>
  );
}

export function CompetitorCardSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <Skeleton className="w-12 h-12 rounded-full" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-5 w-20" />
          </div>
          <Skeleton className="h-4 w-48 mb-2" />
          <Skeleton className="h-3 w-full mb-2" />
          <div className="flex gap-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-20" />
          </div>
        </div>
      </div>
    </Card>
  );
}

export function CompetitorCardEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <TrendingUp className="w-10 h-10 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No competitors added yet</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Add competitors to track their performance
      </p>
    </Card>
  );
}