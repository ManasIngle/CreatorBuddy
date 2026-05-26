"use client";
/**
 * Polling hook for analysis job status.
 *
 * Usage:
 *   const { job, isDone, isFailed } = useJob(jobId);
 *
 * Polls every 3s while job is non-terminal.
 * Stops polling automatically when status is 'done' or 'failed'.
 * On completion, calls onDone/onFailed callbacks if provided.
 */
import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "@/lib/api";
import type { AnalysisJob } from "@/types";

const TERMINAL_STATUSES = new Set(["done", "failed"]);
const POLL_INTERVAL_MS = 3000;

interface UseJobOptions {
  onDone?: (job: AnalysisJob) => void;
  onFailed?: (job: AnalysisJob) => void;
}

export function useJob(jobId: string | null | undefined, options: UseJobOptions = {}) {
  const query = useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => {
      if (!jobId) throw new Error("No job ID");
      const res = await jobsApi.get(jobId);
      return res.data;
    },
    enabled: !!jobId,
    staleTime: 0,                  // always refetch on focus
    gcTime: 5 * 60 * 1000,        // keep in cache 5 min after unmount

    // Refetch every 3s while job is running, stop when terminal
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || TERMINAL_STATUSES.has(status)) return false;
      return POLL_INTERVAL_MS;
    },

    // Fire callbacks on status transitions
    select: (job: AnalysisJob) => {
      if (job.status === "done") options.onDone?.(job);
      if (job.status === "failed") options.onFailed?.(job);
      return job;
    },
  });

  const job = query.data;
  const isDone = job?.status === "done";
  const isFailed = job?.status === "failed";
  const isRunning = job?.status === "running" || job?.status === "queued";

  return {
    job,
    isDone,
    isFailed,
    isRunning,
    progress: job?.progress_pct ?? 0,
    currentStep: (job as (AnalysisJob & { current_step?: string }) | undefined)?.current_step,
    isLoading: query.isLoading,
    error: query.error as Error | null,
  };
}
