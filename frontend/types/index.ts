export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  plan: "free" | "starter" | "pro" | "agency";
  created_at: string;
}

export interface Channel {
  id: string;
  youtube_channel_id: string;
  title: string;
  description: string | null;
  subscriber_count: number;
  video_count: number;
  thumbnail_url: string | null;
  niche: string | null;
  niche_tags: string[];
  audience_type: string | null;
  personality_summary: string | null;
  speaking_style: string | null;
  avg_views: number;
  avg_engagement_rate: number;
  upload_frequency_days: number | null;
  analysis_status: "pending" | "running" | "done" | "failed";
  last_analyzed_at: string | null;
  created_at: string;
}

export interface Competitor {
  id: string;
  youtube_channel_id: string;
  title: string;
  thumbnail_url: string | null;
  subscriber_count: number;
  video_count: number;
  avg_views: number;
  avg_engagement_rate: number;
  niche_overlap_score: number;
  why_they_succeed: string | null;
  best_formats: string[];
  emotional_triggers_used: string[];
  content_gaps: string[];
  hook_patterns: string[];
  thumbnail_style: string | null;
  upload_frequency_days: number | null;
  analysis_status: "pending" | "running" | "done" | "failed";
  last_analyzed_at: string | null;
}

export interface ContentGap {
  id: string;
  topic: string;
  reason: string;
  opportunity_score: number;
  competition_level: "low" | "medium" | "high";
  suggested_angle: string | null;
  suggested_title: string | null;
  trend_direction: "rising" | "stable" | "declining";
  source_type: string;
  is_acted_on: boolean;
  created_at: string;
}

export interface Script {
  id: string;
  topic: string;
  target_duration_minutes: number;
  format_type: string;
  title_suggestions: string[];
  hook: string | null;
  full_script: string | null;
  cta_text: string | null;
  short_form_adaptation: string | null;
  thumbnail_concept: string | null;
  generation_status: "pending" | "generating" | "done" | "failed";
  created_at: string;
}

export interface Hook {
  id: string;
  hook_text: string;
  hook_type: string;
  emotional_trigger: string | null;
  predicted_retention_boost: number | null;
  performance_score: number | null;
}

export interface Trend {
  id: string;
  topic: string;
  niche: string | null;
  velocity_score: number;
  saturation_score: number;
  opportunity_window: "open" | "closing" | "closed";
  recommended_action: string | null;
  first_detected_at: string;
}

export interface AnalysisJob {
  id: string;
  job_type: string;
  status: "queued" | "running" | "done" | "failed";
  progress_pct: number;
}

export interface Video {
  id: string;
  youtube_video_id: string;
  title: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  engagement_rate: number;
  thumbnail_url: string | null;
  published_at: string;
  duration_seconds: number;
  is_viral: boolean;
  transcript: string | null;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
}