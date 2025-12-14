"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { gapsApi } from "@/lib/api";
import type { ContentGap } from "@/types";

export function useContentGaps(channelId: string | undefined) {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["gaps", channelId],
    queryFn: async () => {
      if (!channelId) throw new Error("No channel ID");
      const response = await gapsApi.list(channelId);
      return response.data;
    },
    enabled: !!channelId,
    staleTime: 15 * 60 * 1000, // 15 minutes - gaps analysis is expensive
  });

  const detectGaps = useMutation({
    mutationFn: async () => {
      if (!channelId) throw new Error("No channel ID");
      return gapsApi.detect(channelId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gaps", channelId] });
    },
  });

  return {
    gaps: data || [],
    isLoading,
    error: error as Error | null,
    detectGaps,
  };
}