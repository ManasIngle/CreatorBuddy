"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useStore } from "@/store/useStore";
import Sidebar from "@/components/layout/Sidebar";
import TopBar from "@/components/layout/TopBar";
import { MobileNav } from "./MobileNav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { accessToken } = useStore();
  const router = useRouter();

  useEffect(() => {
    if (!accessToken && !localStorage.getItem("access_token")) {
      router.push("/login");
    }
  }, [accessToken, router]);

  return (
    <div className="flex h-screen bg-surface text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6 pb-20 md:pb-6">
          {children}
        </main>
      </div>
      <MobileNav />
    </div>
  );
}