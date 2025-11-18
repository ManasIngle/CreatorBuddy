"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Search, FileText, Zap, TrendingUp, Settings, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Home", icon: Home },
  { href: "/gaps", label: "Gaps", icon: Search },
  { href: "/competitors", label: "Competitors", icon: BarChart2 },
  { href: "/scripts", label: "Scripts", icon: FileText },
  { href: "/hooks", label: "Hooks", icon: Zap },
  { href: "/trends", label: "Trends", icon: TrendingUp },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface-card border-t border-surface-border md:hidden z-50">
      <div className="flex items-center justify-around py-2 px-2">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg transition-colors",
                isActive
                  ? "text-brand-400"
                  : "text-gray-500 hover:text-gray-300"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}