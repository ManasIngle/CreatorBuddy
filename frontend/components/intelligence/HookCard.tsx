"use client";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Zap, Sparkles, HelpCircle, AlertTriangle, MessageCircle, Crossroads } from "lucide-react";
import type { Hook } from "@/types";

interface HookCardProps {
  hook: Hook;
  onClick?: () => void;
  className?: string;
}

const hookTypeIcons: Record<string, React.ElementType> = {
  curiosity: Sparkles,
  shock: AlertTriangle,
  story: MessageCircle,
  question: HelpCircle,
  contrarian: Crossroads,
};

const hookTypeColors: Record<string, string> = {
  curiosity: "text-accent-yellow",
  shock: "text-accent-red",
  story: "text-accent-purple",
  question: "text-accent-blue",
  contrarian: "text-accent-orange",
};

export function HookCard({ hook, onClick, className }: HookCardProps) {
  const Icon = hookTypeIcons[hook.hook_type] || Zap;
  const color = hookTypeColors[hook.hook_type] || "text-brand-400";

  return (
    <Card
      className={`p-4 cursor-pointer hover:border-brand-600/50 transition group ${className}`}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg bg-surface-elevated ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="subtle" className="text-xs capitalize">
              {hook.hook_type.replace("_", " ")}
            </Badge>
            {hook.emotional_trigger && (
              <Badge variant="brand" className="text-xs">
                {hook.emotional_trigger}
              </Badge>
            )}
          </div>
          <p className="text-gray-300 text-sm line-clamp-3">{hook.hook_text}</p>
        </div>
      </div>

      {hook.predicted_retention_boost && (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-border">
          <Zap className="w-4 h-4 text-accent-green" />
          <span className="text-accent-green text-sm font-medium">
            +{hook.predicted_retention_boost.toFixed(0)}%
          </span>
          <span className="text-gray-500 text-xs">retention boost</span>
        </div>
      )}
    </Card>
  );
}

export function HookCardSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <Skeleton className="w-8 h-8 rounded-lg" />
        <div className="flex-1">
          <div className="flex gap-2 mb-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
      <Skeleton className="h-4 w-32 mt-3 pt-3" />
    </Card>
  );
}

export function HookCardEmpty() {
  return (
    <Card className="p-8 flex flex-col items-center justify-center">
      <Zap className="w-10 h-10 text-gray-600 mb-3" />
      <p className="text-gray-400 text-sm text-center">No hooks generated yet</p>
      <p className="text-gray-500 text-xs text-center mt-1">
        Generate hooks based on a topic
      </p>
    </Card>
  );
}