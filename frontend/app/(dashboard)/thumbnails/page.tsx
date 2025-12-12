"use client";
import { useState } from "react";
import { thumbnailsApi } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { ThumbnailAnalysis, ThumbnailAnalysisSkeleton, ThumbnailAnalysisEmpty } from "@/components/intelligence/ThumbnailAnalysis";
import { Image, Search, Sparkles, RefreshCw, Palette } from "lucide-react";

interface AnalysisResult {
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
}

export default function ThumbnailsPage() {
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("analyze");
  const [history, setHistory] = useState<Array<{ url: string; title: string; analysis: AnalysisResult }>>([]);

  const handleAnalyze = async () => {
    if (!thumbnailUrl.trim() || !videoTitle.trim()) return;
    setLoading(true);
    try {
      const response = await thumbnailsApi.analyze(thumbnailUrl, videoTitle);
      setAnalysis(response.data);
      setHistory((prev) => [{ url: thumbnailUrl, title: videoTitle, analysis: response.data }, ...prev.slice(0, 9)]);
    } catch (e) {
      console.error("Failed to analyze thumbnail", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Thumbnail Intelligence</h1>
        <p className="text-gray-400 text-sm mt-1">
          AI-powered thumbnail analysis and recommendations
        </p>
      </div>

      <Tabs
        tabs={[
          { key: "analyze", label: "Analyze Thumbnail" },
          { key: "history", label: "Analysis History" },
        ]}
        activeTab={activeTab}
        onChange={(id) => setActiveTab(id as "analyze" | "history")}
      />

      {activeTab === "analyze" && (
        <>
          {/* Analyze Form */}
          <Card className="p-5">
            <div className="space-y-4">
              <div>
                <label className="text-white text-sm font-medium block mb-2">
                  Thumbnail URL
                </label>
                <Input
                  value={thumbnailUrl}
                  onChange={(e) => setThumbnailUrl(e.target.value)}
                  placeholder="https://i.ytimg.com/vi/..."
                />
              </div>
              <div>
                <label className="text-white text-sm font-medium block mb-2">
                  Video Title
                </label>
                <Input
                  value={videoTitle}
                  onChange={(e) => setVideoTitle(e.target.value)}
                  placeholder="Enter the video title..."
                />
              </div>
              <Button
                onClick={handleAnalyze}
                disabled={loading || !thumbnailUrl.trim() || !videoTitle.trim()}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                {loading ? "Analyzing..." : "Analyze Thumbnail"}
              </Button>
            </div>
          </Card>

          {/* Result */}
          {loading ? (
            <ThumbnailAnalysisSkeleton />
          ) : analysis ? (
            <ThumbnailAnalysis
              thumbnail_url={thumbnailUrl}
              video_title={videoTitle}
              analysis={analysis}
            />
          ) : (
            <ThumbnailAnalysisEmpty />
          )}
        </>
      )}

      {activeTab === "history" && (
        <div className="space-y-4">
          {history.length === 0 ? (
            <Card className="p-8 flex flex-col items-center justify-center">
              <Image className="w-12 h-12 text-gray-600 mb-3" />
              <p className="text-gray-400 text-sm text-center">No analysis history</p>
              <p className="text-gray-500 text-xs text-center mt-1">
                Analyze thumbnails to build history
              </p>
            </Card>
          ) : (
            history.map((item, i) => (
              <ThumbnailAnalysis
                key={i}
                thumbnail_url={item.url}
                video_title={item.title}
                analysis={item.analysis}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}