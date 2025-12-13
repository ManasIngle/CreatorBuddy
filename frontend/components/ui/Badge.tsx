import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "purple" | "orange";
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    const variants = {
      default: "bg-brand-600/20 text-brand-400 border-brand-600/30",
      success: "bg-accent-green/10 text-accent-green border-accent-green/30",
      warning: "bg-accent-yellow/10 text-accent-yellow border-accent-yellow/30",
      danger: "bg-accent-red/10 text-accent-red border-accent-red/30",
      purple: "bg-accent-purple/10 text-accent-purple border-accent-purple/30",
      orange: "bg-accent-orange/10 text-accent-orange border-accent-orange/30",
    };

    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);
Badge.displayName = "Badge";