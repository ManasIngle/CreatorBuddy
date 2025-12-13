"use client";
import { useStore } from "@/store/useStore";
import { Bell, Search } from "lucide-react";

export default function TopBar() {
  const { activeChannel, user } = useStore();

  return (
    <header className="h-16 bg-surface-card border-b border-surface-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {activeChannel && (
          <div className="flex items-center gap-2">
            {activeChannel.thumbnail_url && (
              <img 
                src={activeChannel.thumbnail_url} 
                alt={activeChannel.title}
                className="w-8 h-8 rounded-full"
              />
            )}
            <span className="text-white font-medium text-sm">{activeChannel.title}</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-400 hover:text-white transition">
          <Search className="w-5 h-5" />
        </button>
        <button className="p-2 text-gray-400 hover:text-white transition relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-brand-500 rounded-full" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-brand-600/30 flex items-center justify-center text-brand-400 text-sm font-semibold">
            {user?.full_name?.[0] || user?.email?.[0]?.toUpperCase() || "?"}
          </div>
        </div>
      </div>
    </header>
  );
}