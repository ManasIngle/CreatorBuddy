"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { scriptsApi } from "@/lib/api";
import type { Script } from "@/types";

export function useScripts() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ["scripts"],
    queryFn: async () => {
      const response = await scriptsApi.list();
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  return {
    scripts: data || [],
    isLoading,
    error: error as Error | null,
  };
}

export function useScript(scriptId: string | undefined) {
  return useQuery({
    queryKey: ["script", scriptId],
    queryFn: async () => {
      if (!scriptId) throw new Error("No script ID");
      const response = await scriptsApi.get(scriptId);
      return response.data;
    },
    enabled: !!scriptId,
    staleTime: 5 * 60 * 1000,
  });
}

interface GenerateScriptParams {
  topic: string;
  channel_id?: string;
  target_duration_minutes?: number;
  format_type?: string;
}

export function useGenerateScript() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: GenerateScriptParams) => {
      const response = await scriptsApi.generate(params);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scripts"] });
    },
  });
}

export function useDeleteScript() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (scriptId: string) => {
      return scriptsApi.delete(scriptId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scripts"] });
    },
  });
}