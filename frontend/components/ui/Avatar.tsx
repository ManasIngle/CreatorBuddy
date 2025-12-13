import React from "react";
import { cn } from "@/lib/utils";

export interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export function Avatar({ src, alt, fallback, size = "md", className }: AvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-12 h-12 text-base",
    xl: "w-16 h-16 text-lg",
  };

  return (
    <div
      className={cn(
        "rounded-full bg-brand-600/30 flex items-center justify-center text-brand-400 font-semibold overflow-hidden",
        sizeClasses[size],
        className
      )}
    >
      {src ? (
        <img src={src} alt={alt || "Avatar"} className="w-full h-full object-cover" />
      ) : (
        fallback?.[0]?.toUpperCase() || "?"
      )}
    </div>
  );
}