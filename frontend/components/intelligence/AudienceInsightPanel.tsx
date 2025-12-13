"use client";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Brain, Users, Heart, MessageCircle, TrendingUp } from "lucide-react";

interface AudienceInsight {
  demographics?: {
    age_range: string;
    top_countries: string[];
    gender_split: string;
  };
  psychology?: {
    primary_motivation: string;
    pain_points: string[];
    desires: string[];
    content_expectations: string[];
  };
  behavior?: {
    peak_watch_times: string[];
    avg_session_duration: string;
    typical_finish_rate: string;
    comment_frequency: string;
  };
}

interface AudienceInsightPanelProps {
  insights: AudienceInsight;
  className?: string;
}

export function AudienceInsightPanel({ insights, className }: AudienceInsightPanelProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Demographics */}
      {insights.demographics && (
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="w-4 h-4 text-brand-400" />
            <h3 className="text-white font-medium">Demographics</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400 text-sm">Age Range</span>
              <span className="text-white text-sm">{insights.demographics.age_range}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400 text-sm">Gender Split</span>
              <span className="text-white text-sm">{insights.demographics.gender_split}</span>
            </div>
            <div className="pt-2">
              <span className="text-gray-400 text-sm block mb-1">Top Countries</span>
              <div className="flex flex-wrap gap-1">
                {insights.demographics.top_countries.map((country) => (
                  <Badge key={country} variant="subtle" className="text-xs">
                    {country}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Psychology */}
      {insights.psychology && (
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="w-4 h-4 text-accent-purple" />
            <h3 className="text-white font-medium">Audience Psychology</h3>
          </div>
          <div className="space-y-3">
            <div>
              <span className="text-gray-500 text-xs block mb-1">Primary Motivation</span>
              <p className="text-gray-300 text-sm">{insights.psychology.primary_motivation}</p>
            </div>
            <div>
              <span className="text-gray-500 text-xs block mb-1">Pain Points</span>
              <ul className="space-y-1">
                {insights.psychology.pain_points.map((point, i) => (
                  <li key={i} className="text-gray-400 text-xs flex items-start gap-1">
                    <span className="text-accent-red">•</span> {point}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <span className="text-gray-500 text-xs block mb-1">What They Want</span>
              <ul className="space-y-1">
                {insights.psychology.desires.map((desire, i) => (
                  <li key={i} className="text-gray-400 text-xs flex items-start gap-1">
                    <span className="text-accent-green">•</span> {desire}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Behavior */}
      {insights.behavior && (
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-accent-green" />
            <h3 className="text-white font-medium">Watch Behavior</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-2 bg-surface-elevated rounded-lg">
              <span className="text-gray-500 text-xs block">Peak Times</span>
              <p className="text-white text-sm">
                {insights.behavior.peak_watch_times.join(", ")}
              </p>
            </div>
            <div className="p-2 bg-surface-elevated rounded-lg">
              <span className="text-gray-500 text-xs block">Avg Session</span>
              <p className="text-white text-sm">{insights.behavior.avg_session_duration}</p>
            </div>
            <div className="p-2 bg-surface-elevated rounded-lg">
              <span className="text-gray-500 text-xs block">Finish Rate</span>
              <p className="text-white text-sm">{insights.behavior.typical_finish_rate}</p>
            </div>
            <div className="p-2 bg-surface-elevated rounded-lg">
              <span className="text-gray-500 text-xs block">Comment Frequency</span>
              <p className="text-white text-sm">{insights.behavior.comment_frequency}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

export function AudienceInsightPanelSkeleton() {
  return (
    <div className="space-y-4">
      <Card className="p-4">
        <Skeleton className="h-5 w-32 mb-3" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </Card>
      <Card className="p-4">
        <Skeleton className="h-5 w-40 mb-3" />
        <Skeleton className="h-20 w-full" />
      </Card>
    </div>
  );
}

export function AudienceInsightPanelEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <Brain className="w-10 h-10 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No audience insights available</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Complete channel analysis to see insights
      </p>
    </Card>
  );
}