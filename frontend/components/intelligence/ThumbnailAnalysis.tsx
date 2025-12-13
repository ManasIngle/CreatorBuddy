"use client";
import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Progress } from "@/components/ui/Progress";
import { Skeleton } from "@/components/ui/Skeleton";
import { Image, Eye, MousePointer, Palette, AlertCircle, CheckCircle2, X } from "lucide-react";

interface ThumbnailAnalysisProps {
  thumbnail_url: string;
  video_title: string;
  analysis?: {
    ctr_prediction: number;
    emotional_impact: number;
    curiosity_intensity: number;
    text_clarity: number;
    color_contrast: number;
    simplicity: number;
    alignment_score: number;
    primary_emotion: string;
    strengths: string[];
    weaknesses: string[];
    improvement_suggestions: string[];
  };
  loading?: boolean;
  className?: string;
}

export function ThumbnailAnalysis({
  thumbnail_url,
  video_title,
  analysis,
  loading,
  className,
}: ThumbnailAnalysisProps) {
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  if (loading) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="flex gap-4">
          <Skeleton className="w-48 h-32 rounded-lg" />
          <div className="flex-1 space-y-3">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex gap-2 mt-4">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-24" />
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card className={`p-6 flex flex-col items-center justify-center ${className}`}>
        <Image className="w-12 h-12 text-gray-600 mb-3" />
        <p className="text-gray-400 text-sm text-center">No analysis available</p>
        <p className="text-gray-500 text-xs text-center mt-1">
          Analyze a thumbnail to see AI insights
        </p>
      </Card>
    );
  }

  const overallScore = (
    analysis.emotional_impact +
    analysis.curiosity_intensity +
    analysis.text_clarity +
    analysis.color_contrast +
    analysis.simplicity +
    analysis.alignment_score
  ) / 6;

  const scoreColor = overallScore >= 7
    ? "text-accent-green"
    : overallScore >= 5
    ? "text-accent-yellow"
    : "text-accent-orange";

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex gap-4">
        <div className="relative w-48 flex-shrink-0">
          <img
            src={thumbnail_url}
            alt={video_title}
            className="w-full h-32 object-cover rounded-lg"
          />
          <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs text-white font-medium">
            CTR: {analysis.ctr_prediction.toFixed(1)}/10
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-medium text-sm truncate">{video_title}</h3>
            <div className={`text-2xl font-bold ${scoreColor}`}>
              {overallScore.toFixed(1)}
            </div>
          </div>

          <p className="text-gray-400 text-xs mb-3">
            Primary emotion: <span className="text-white">{analysis.primary_emotion}</span>
          </p>

          <div className="grid grid-cols-3 gap-2 mb-3">
            {[
              { label: "Emotion", value: analysis.emotional_impact, icon: AlertCircle },
              { label: "Curiosity", value: analysis.curiosity_intensity, icon: Eye },
              { label: "Contrast", value: analysis.color_contrast, icon: Palette },
            ].map((metric) => (
              <div key={metric.label} className="flex items-center gap-1.5">
                <metric.icon className="w-3 h-3 text-gray-500" />
                <Progress value={metric.value * 10} className="flex-1 h-1.5" />
                <span className="text-gray-400 text-xs w-4">{metric.value}</span>
              </div>
            ))}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFullAnalysis(!showFullAnalysis)}
          >
            {showFullAnalysis ? "Hide Details" : "Show Details"}
          </Button>
        </div>
      </div>

      {showFullAnalysis && (
        <div className="mt-4 pt-4 border-t border-surface-border">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-accent-green text-sm font-medium mb-2 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" /> Strengths
              </h4>
              <ul className="space-y-1">
                {analysis.strengths.map((s, i) => (
                  <li key={i} className="text-gray-400 text-xs">• {s}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-accent-orange text-sm font-medium mb-2 flex items-center gap-1">
                <X className="w-4 h-4" /> Weaknesses
              </h4>
              <ul className="space-y-1">
                {analysis.weaknesses.map((w, i) => (
                  <li key={i} className="text-gray-400 text-xs">• {w}</li>
                ))}
              </ul>
            </div>
          </div>

          {analysis.improvement_suggestions.length > 0 && (
            <div className="mt-4 p-3 bg-surface-elevated rounded-lg">
              <h4 className="text-white text-sm font-medium mb-2">Suggestions</h4>
              <ul className="space-y-1">
                {analysis.improvement_suggestions.map((s, i) => (
                  <li key={i} className="text-gray-300 text-xs">💡 {s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export function ThumbnailAnalysisSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex gap-4">
        <Skeleton className="w-48 h-32 rounded-lg" />
        <div className="flex-1">
          <Skeleton className="h-6 w-32 mb-2" />
          <Skeleton className="h-4 w-full mb-4" />
          <div className="flex gap-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-8 w-20" />
          </div>
        </div>
      </div>
    </Card>
  );
}

export function ThumbnailAnalysisEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <Image className="w-12 h-12 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No thumbnail analysis</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Enter a thumbnail URL to analyze
      </p>
    </Card>
  );
}