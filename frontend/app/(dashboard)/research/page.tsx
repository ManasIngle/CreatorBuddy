"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { api } from "@/lib/api";

interface ResearchResult {
  topic?: string;
  niche?: string;
  sources?: any[];
  ai_synthesis?: string;
  comprehensive_briefing?: string;
  success?: boolean;
}

interface Source {
  source?: string;
  forum_type?: string;
  subreddit?: string;
  content?: string;
  scraped_at?: string;
}

export default function ResearchPage() {
  const [topic, setTopic] = useState("");
  const [niche, setNiche] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ResearchResult | null>(null);
  const [activeTab, setActiveTab] = useState("topic");

  const handleDeepResearch = async () => {
    if (!topic || !niche) return;

    setLoading(true);
    try {
      const response = await api.post("/research/deep-research", {
        topic,
        niche,
        sources_count: 10,
      });
      setResults(response.data);
    } catch (error) {
      console.error("Research failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicResearch = async () => {
    if (!topic || !niche) return;

    setLoading(true);
    setActiveTab("topic");
    try {
      const response = await api.post("/research/topic", {
        topic,
        niche,
        depth: "deep",
      });
      setResults(response.data);
    } catch (error) {
      console.error("Topic research failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompetitorResearch = async () => {
    if (!topic) return;

    setLoading(true);
    setActiveTab("competitor");
    try {
      const response = await api.post("/research/competitor", {
        competitor_name: topic,
        include_social: true,
      });
      setResults(response.data);
    } catch (error) {
      console.error("Competitor research failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendsResearch = async () => {
    if (!niche) return;

    setLoading(true);
    setActiveTab("trends");
    try {
      const response = await api.post("/research/trends", {
        niche,
        time_range: "week",
      });
      setResults(response.data);
    } catch (error) {
      console.error("Trends research failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAudienceResearch = async () => {
    if (!topic) return;

    setLoading(true);
    setActiveTab("audience");
    try {
      const response = await api.post("/research/audience", {
        topic,
        include_forums: true,
        include_reddit: true,
        include_quora: true,
      });
      setResults(response.data);
    } catch (error) {
      console.error("Audience research failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatSource = (source: Source) => {
    if (source.subreddit) return `r/${source.subreddit}`;
    if (source.forum_type) return source.forum_type;
    if (source.source) {
      try {
        const url = new URL(source.source);
        return url.hostname;
      } catch {
        return source.source;
      }
    }
    return "Unknown source";
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold">Research Dashboard</h1>
        <p className="text-muted-foreground">
          Aggressive web scraping for real-time intelligence gathering
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Research Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Topic / Keyword</label>
              <Input
                placeholder="e.g., AI video editing, fitness tips"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Niche</label>
              <Input
                placeholder="e.g., technology, health, finance"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={handleDeepResearch} disabled={loading || !topic || !niche}>
              {loading ? "Researching..." : "Deep Research (10+ sources)"}
            </Button>
            <Button onClick={handleTopicResearch} disabled={loading || !topic || !niche} variant="outline">
              Topic Research
            </Button>
            <Button onClick={handleCompetitorResearch} disabled={loading || !topic} variant="outline">
              Competitor Intel
            </Button>
            <Button onClick={handleTrendsResearch} disabled={loading || !niche} variant="outline">
              Trend Analysis
            </Button>
            <Button onClick={handleAudienceResearch} disabled={loading || !topic} variant="outline">
              Audience Insights
            </Button>
          </div>
        </CardContent>
      </Card>

      {results && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="topic">Topic Analysis</TabsTrigger>
            <TabsTrigger value="sources">Sources ({results.sources?.length || 0})</TabsTrigger>
            <TabsTrigger value="ai">AI Synthesis</TabsTrigger>
          </TabsList>

          <TabsContent value="topic" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{results.topic || results.niche} Research</span>
                  <Badge variant={results.success ? "default" : "destructive"}>
                    {results.success ? "Success" : "Partial"}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {results.comprehensive_briefing && (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg">
                      {results.comprehensive_briefing}
                    </pre>
                  </div>
                )}
                {results.ai_synthesis && (
                  <div className="mt-4">
                    <h3 className="font-semibold mb-2">AI Synthesis</h3>
                    <div className="bg-muted p-4 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm">
                        {results.ai_synthesis}
                      </pre>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sources" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Scraped Sources ({results.sources?.length || 0})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.sources?.map((source: Source, index: number) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline">
                          {formatSource(source)}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {source.scraped_at ? new Date(source.scraped_at).toLocaleString() : ""}
                        </span>
                      </div>
                      <p className="text-sm line-clamp-3">
                        {source.content?.substring(0, 300)}...
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>AI-Generated Insights</CardTitle>
              </CardHeader>
              <CardContent>
                {results.ai_synthesis ? (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg">
                      {results.ai_synthesis}
                    </pre>
                  </div>
                ) : results.comprehensive_briefing ? (
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg">
                      {results.comprehensive_briefing}
                    </pre>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No AI synthesis available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Available Scraping Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Badge>Reddit</Badge>
              <span className="text-sm text-muted-foreground">Trends, discussions</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge>Quora</Badge>
              <span className="text-sm text-muted-foreground">Questions, topics</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge>Google</Badge>
              <span className="text-sm text-muted-foreground">Search, trends, SEO</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge>Wikipedia</Badge>
              <span className="text-sm text-muted-foreground">Topics, concepts</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge>YouTube</Badge>
              <span className="text-sm text-muted-foreground">Channels, content</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge>News</Badge>
              <span className="text-sm text-muted-foreground">Breaking, trends</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Scraping Capabilities</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>• Real-time trend detection from Twitter, Reddit, news</li>
            <li>• Cross-platform intelligence from YouTube, social media, blogs</li>
            <li>• Audience pulse with real questions from forums</li>
            <li>• Competitor monitoring with ongoing scraping</li>
            <li>• Content ideation from Wikipedia, research, discussions</li>
            <li>• SERP analysis for target keywords</li>
            <li>• Graceful degradation with fallback to YouTube API</li>
            <li>• 30-second timeout per scrape with rate limiting</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}