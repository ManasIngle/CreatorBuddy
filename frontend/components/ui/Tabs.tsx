import React from "react";
import { cn } from "@/lib/utils";

export interface TabItem {
  id: string;
  label: string;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div className={cn("flex border-b border-surface-border", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            "px-5 py-3 text-sm font-medium transition",
            activeTab === tab.id
              ? "text-brand-400 border-b-2 border-brand-500 bg-brand-600/5"
              : "text-gray-400 hover:text-white"
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}