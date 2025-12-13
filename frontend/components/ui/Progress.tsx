import React from "react";
import { cn } from "@/lib/utils";

export interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
}

export function Progress({ value, max = 100, className }: ProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className={cn("w-full h-2 rounded-full bg-surface-border overflow-hidden", className)}>
      <div 
        className="h-full bg-gradient-to-r from-brand-500 to-brand-600 transition-all duration-500"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}