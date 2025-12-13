"use client";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { TrendingUp, Users, Eye, Zap } from "lucide-react";
import type { Channel } from "@/types";

interface CreatorProfileCardProps {
  channel: Channel;
  className?: string;
}

export function CreatorProfileCard({ channel, className }: CreatorProfileCardProps) {
  const stats = [
    { label: "Subscribers", value: channel.subscriber_count.toLocaleString(), icon: Users },
    { label: "Avg Views", value: Math.round(channel.avg_views).toLocaleString(), icon: Eye },
    { label: "Engagement", value: `${(channel.avg_engagement_rate * 100).toFixed(1)}%`, icon: TrendingUp },
  ];

  return (
    <Card className={`p-5 ${className}`}>
      <div className="flex items-start gap-4">
        <Avatar
          src={channel.thumbnail_url}
          alt={channel.title}
          size="xl"
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate">{channel.title}</h3>
          <div className="flex flex-wrap gap-2 mt-2">
            {channel.niche && (
              <Badge variant="brand">{channel.niche}</Badge>
            )}
            {channel.niche_tags?.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="subtle">{tag}</Badge>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-4">
        {stats.map((stat) => (
          <div key={stat.label} className="text-center p-3 bg-surface-elevated rounded-lg">
            <stat.icon className="w-4 h-4 text-brand-400 mx-auto mb-1" />
            <p className="text-white text-sm font-semibold">{stat.value}</p>
            <p className="text-gray-500 text-xs">{stat.label}</p>
          </div>
        ))}
      </div>

      {channel.personality_summary && (
        <div className="mt-4 pt-4 border-t border-surface-border">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-accent-orange" />
            <span className="text-white text-sm font-medium">AI Insights</span>
          </div>
          <p className="text-gray-400 text-sm">{channel.personality_summary}</p>
        </div>
      )}

      {channel.speaking_style && (
        <div className="mt-3">
          <p className="text-gray-500 text-xs">
            <span className="text-gray-400 font-medium">Speaking style:</span> {channel.speaking_style}
          </p>
        </div>
      )}
    </Card>
  );
}

export function CreatorProfileCardSkeleton() {
  return (
    <Card className="p-5">
      <div className="flex items-start gap-4">
        <Skeleton className="w-16 h-16 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-5 w-40 mb-2" />
          <div className="flex gap-2">
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-5 w-20" />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3 mt-4">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-16" />
        ))}
      </div>
    </Card>
  );
}

export function CreatorProfileCardEmpty() {
  return (
    <Card className="p-5 flex items-center justify-center h-32">
      <p className="text-gray-500 text-sm">No channel data available</p>
    </Card>
  );
}