"use client";
import { useQuery } from "@tanstack/react-query";
import { channelsApi } from "@/lib/api";
import type { Channel } from "@/types";

interface UseCreatorProfileResult {
  channels: Channel[];
  activeChannel: Channel | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useCreatorProfile(): UseCreatorProfileResult {
  const { data, isLoading, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ["channels"],
    queryFn: async () => {
      const response = await channelsApi.list();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  return {
    channels: data || [],
    activeChannel: data?.[0] || null,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}

export function useChannel(channelId: string | undefined) {
  return useQuery({
    queryKey: ["channel", channelId],
    queryFn: async () => {
      if (!channelId) throw new Error("No channel ID");
      const response = await channelsApi.get(channelId);
      return response.data;
    },
    enabled: !!channelId,
    staleTime: 5 * 60 * 1000,
  });
}