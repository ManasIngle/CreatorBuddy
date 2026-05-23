"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import {
  LayoutDashboard, Youtube, Users, Search,
  FileText, Zap, Image, TrendingUp, Settings, LogOut
} from "lucide-react";
import { useStore } from "@/store/useStore";
import { useRouter } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/channel", label: "My Channel", icon: Youtube },
  { href: "/competitors", label: "Competitors", icon: Users },
  { href: "/gaps", label: "Content Gaps", icon: Search },
  { href: "/scripts", label: "Scripts", icon: FileText },
  { href: "/hooks", label: "Hooks", icon: Zap },
  { href: "/thumbnails", label: "Thumbnails", icon: Image },
  { href: "/trends", label: "Trends", icon: TrendingUp },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useStore();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <aside className="w-64 bg-surface-card border-r border-surface-border flex flex-col">
      <div className="p-6 border-b border-surface-border">
        <span className="text-xl font-bold bg-gradient-brand bg-clip-text text-transparent">
          CreatorIQ
        </span>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-brand-600/20 text-brand-400 border border-brand-600/30"
                : "text-gray-400 hover:bg-surface hover:text-white"
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-surface-border">
        {user?.plan === "free" && (
          <div className="bg-gradient-to-r from-brand-600 to-indigo-600 p-4 rounded-xl mb-4 text-white space-y-2 border border-brand-500/30 shadow-lg relative overflow-hidden group">
            <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            <h4 className="font-semibold text-xs flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-brand-300 animate-pulse" />
              Unlock Pro Features
            </h4>
            <p className="text-[10px] text-brand-100 leading-relaxed">
              Get unlimited scripts, competitor tracking & deeper research.
            </p>
            <Link
              href="/settings?upgrade=true"
              className="block w-full text-center bg-white text-brand-600 font-semibold text-[11px] py-1.5 rounded-lg hover:bg-brand-50 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              Upgrade Now
            </Link>
          </div>
        )}
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-brand-600/30 flex items-center justify-center text-brand-400 text-sm font-semibold">
            {user?.full_name?.[0] || user?.email?.[0]?.toUpperCase() || "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.full_name || "Creator"}</p>
            <p className="text-gray-500 text-xs capitalize">{user?.plan} plan</p>
          </div>
        </div>
        <Link
          href="/settings"
          className="flex items-center gap-2 text-gray-400 hover:text-white text-sm px-2 py-1.5 rounded transition"
        >
          <Settings className="w-4 h-4" /> Settings
        </Link>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-gray-400 hover:text-red-400 text-sm px-2 py-1.5 rounded transition w-full"
        >
          <LogOut className="w-4 h-4" /> Sign out
        </button>
      </div>
    </aside>
  );
}