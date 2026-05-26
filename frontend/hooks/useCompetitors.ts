"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { competitorsApi } from "@/lib/api";
import type { Competitor } from "@/types";

export function useCompetitors(channelId: string | undefined) {
  const queryClient = useQueryClient();

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ["competitors", channelId],
    queryFn: async () => {
      if (!channelId) throw new Error("No channel ID");
      const response = await competitorsApi.list(channelId);
      return response.data;
    },
    enabled: !!channelId,
    // Stale time of 10 minutes - data is considered fresh
    // If stale, returns cached data while refetching in background (stale-while-revalidate)
    staleTime: 10 * 60 * 1000,
    // Cache for 30 minutes - keep in memory even if not subscribed
    gcTime: 30 * 60 * 1000,
    // Refetch on window focus for fresh data
    refetchOnWindowFocus: true,
    // Retry failed requests up to 2 times
    retry: 2,
  });

  const addCompetitor = useMutation({
    mutationFn: async (youtube_channel_id: string) => {
      if (!channelId) throw new Error("No channel ID");
      return competitorsApi.add(channelId, youtube_channel_id);
    },
    onSuccess: () => {
      // Optimistically update cache then refetch
      queryClient.invalidateQueries({ queryKey: ["competitors", channelId] });
    },
    onError: () => {
      // On error, refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ["competitors", channelId] });
    },
  });

  return {
    competitors: data || [],
    isLoading,
    isFetching,
    error: error as Error | null,
    addCompetitor,
  };
}

export function useCompetitor(channelId: string | undefined, competitorId: string | undefined) {
  return useQuery({
    queryKey: ["competitor", channelId, competitorId],
    queryFn: async () => {
      if (!channelId || !competitorId) throw new Error("Missing IDs");
      const response = await competitorsApi.get(channelId, competitorId);
      return response.data;
    },
    enabled: !!channelId && !!competitorId,
    staleTime: 5 * 60 * 1000, // 5 minutes - competitor data changes less frequently
    gcTime: 15 * 60 * 1000,
    retry: 2,
  });
}

// Hook for refreshing competitor data on demand
export function useRefreshCompetitors(channelId: string | undefined) {
  const queryClient = useQueryClient();

  return {
    refresh: () => {
      if (channelId) {
        queryClient.invalidateQueries({ queryKey: ["competitors", channelId] });
      }
    },
    refreshAll: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
    },
  };
}