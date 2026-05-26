/**
 * Typed API client for CreatorIQ.
 *
 * Architecture decisions:
 *  - Single axios instance, base URL from env.
 *  - JWT injected via request interceptor (reads from localStorage).
 *  - On 401 → clear token + redirect to /login.
 *  - On 429/5xx → retry with exponential backoff (max 3 attempts).
 *  - All sub-APIs are plain objects — no classes, easy to tree-shake.
 */

import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { getStoredToken, clearToken } from "./auth";
import type {
  User,
  Channel,
  Competitor,
  ContentGap,
  Script,
  Hook,
  Trend,
  AnalysisJob,
} from "@/types";

// ---------------------------------------------------------------------------
// Core instance
// ---------------------------------------------------------------------------

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000, // 60s — script generation is slow
  headers: { "Content-Type": "application/json" },
});

// Inject JWT on every request
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getStoredToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors + retry on transient failures
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const config = error.config as AxiosRequestConfig & {
      _retryCount?: number;
    };

    // 401 → clear token and redirect (only in browser)
    if (error.response?.status === 401) {
      clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    // Retry on 429 or 5xx — up to 3 attempts with exp backoff
    const retryable =
      error.response?.status === 429 ||
      (error.response?.status >= 500 && error.response?.status < 600) ||
      error.code === "ECONNABORTED";

    config._retryCount = config._retryCount ?? 0;

    if (retryable && config._retryCount < 3) {
      config._retryCount += 1;
      const delay = Math.min(1000 * 2 ** config._retryCount, 10_000);
      await new Promise((r) => setTimeout(r, delay));
      return api(config);
    }

    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Response type helpers
// ---------------------------------------------------------------------------

type R<T> = Promise<AxiosResponse<T>>;

// Pagination envelope returned by list endpoints
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const authApi = {
  register: (email: string, password: string, full_name?: string): R<User> =>
    api.post("/auth/register", { email, password, full_name }),

  login: (
    email: string,
    password: string
  ): R<{ access_token: string; token_type: string }> => {
    // FastAPI OAuth2 password flow expects form data
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: (): R<User> => api.get("/auth/me"),

  updatePlan: (plan: "free" | "starter" | "pro" | "agency"): R<User> =>
    api.put("/auth/plan", { plan }),

  googleCallback: (code: string): R<{ access_token: string; user: User }> =>
    api.post("/auth/google/callback", null, { params: { code } }),
};

// ---------------------------------------------------------------------------
// Channels API
// ---------------------------------------------------------------------------

export const channelsApi = {
  list: (
    page = 1,
    page_size = 50
  ): R<PaginatedResponse<Channel>> =>
    api.get("/channels/", { params: { page, page_size } }),

  get: (channel_id: string): R<Channel> =>
    api.get(`/channels/${channel_id}`),

  connect: (youtube_channel_id: string): R<Channel> =>
    api.post("/channels/connect", { youtube_channel_id }),

  reanalyze: (channel_id: string): R<{ message: string }> =>
    api.post(`/channels/${channel_id}/re-analyze`),
};

// ---------------------------------------------------------------------------
// Competitors API
// ---------------------------------------------------------------------------

export const competitorsApi = {
  list: (channel_id: string): R<Competitor[]> =>
    api.get(`/competitors/${channel_id}/`),

  get: (channel_id: string, competitor_id: string): R<Competitor> =>
    api.get(`/competitors/${channel_id}/${competitor_id}`),

  add: (channel_id: string, youtube_channel_id: string): R<Competitor> =>
    api.post(`/competitors/${channel_id}/add`, { youtube_channel_id }),

  remove: (channel_id: string, competitor_id: string): R<void> =>
    api.delete(`/competitors/${channel_id}/${competitor_id}`),
};

// ---------------------------------------------------------------------------
// Gaps API
// ---------------------------------------------------------------------------

export const gapsApi = {
  list: (channel_id: string): R<ContentGap[]> =>
    api.get(`/gaps/${channel_id}/`),

  detect: (channel_id: string): R<ContentGap[]> =>
    api.post(`/gaps/${channel_id}/detect`),

  markActedOn: (channel_id: string, gap_id: string): R<ContentGap> =>
    api.post(`/gaps/${channel_id}/gaps/${gap_id}/acted-on`),
};

// ---------------------------------------------------------------------------
// Scripts API
// ---------------------------------------------------------------------------

interface GenerateScriptParams {
  topic: string;
  channel_id?: string;
  target_duration_minutes?: number;
  format_type?: string;
  tone?: string;
}

export const scriptsApi = {
  list: (): R<Script[]> => api.get("/scripts/"),

  get: (script_id: string): R<Script> => api.get(`/scripts/${script_id}`),

  generate: (params: GenerateScriptParams): R<Script> =>
    api.post("/scripts/generate", params),

  delete: (script_id: string): R<void> =>
    api.delete(`/scripts/${script_id}`),
};

// ---------------------------------------------------------------------------
// Hooks API
// ---------------------------------------------------------------------------

export const hooksApi = {
  list: (channel_id?: string): R<Hook[]> =>
    api.get("/hooks/", { params: channel_id ? { channel_id } : {} }),

  generate: (channel_id: string, topic: string, count = 5): R<Hook[]> =>
    api.post("/hooks/generate", { channel_id, topic, count }),
};

// ---------------------------------------------------------------------------
// Thumbnails API
// ---------------------------------------------------------------------------

export const thumbnailsApi = {
  analyze: (
    thumbnail_url: string,
    video_title: string
  ): R<{
    ctr_prediction: number;
    emotional_impact: number;
    text_clarity: number;
    strengths: string[];
    weaknesses: string[];
    improvement_suggestions: string[];
  }> =>
    api.post("/thumbnails/analyze", { thumbnail_url, video_title }),
};

// ---------------------------------------------------------------------------
// Trends API
// ---------------------------------------------------------------------------

export const trendsApi = {
  list: (niche?: string): R<Trend[]> =>
    api.get("/trends/", { params: niche ? { niche } : {} }),

  detect: (niche: string): R<Trend[]> =>
    api.post("/trends/detect", { niche }),
};

// ---------------------------------------------------------------------------
// Research API
// ---------------------------------------------------------------------------

interface ResearchResult {
  topic: string;
  niche: string;
  sources: unknown[];
  insights: Record<string, unknown>;
  success: boolean;
}

export const researchApi = {
  deepResearch: (topic: string, niche: string): R<ResearchResult> =>
    api.post("/research/deep-research", { topic, niche }),

  topic: (topic: string, niche: string): R<ResearchResult> =>
    api.post("/research/topic", { topic, niche }),

  competitor: (competitor_name: string): R<ResearchResult> =>
    api.post("/research/competitor", { competitor_name, include_social: true }),

  trends: (niche: string): R<ResearchResult> =>
    api.post("/research/trends", { niche, time_range: "week" }),

  audience: (topic: string): R<ResearchResult> =>
    api.post("/research/audience", { topic, include_forums: true }),
};

// ---------------------------------------------------------------------------
// Jobs API  (polling for analysis status)
// ---------------------------------------------------------------------------

export const jobsApi = {
  get: (job_id: string): R<AnalysisJob> => api.get(`/jobs/${job_id}`),
};

// ---------------------------------------------------------------------------
// Usage / billing
// ---------------------------------------------------------------------------

export const usageApi = {
  status: (): R<{
    tokens_used: number;
    token_limit: number;
    percentage: number;
    remaining: number;
    status: "ok" | "warning" | "critical";
    plan: string;
  }> => api.get("/auth/usage"),
};
