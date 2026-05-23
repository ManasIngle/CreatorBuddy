"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import type { Channel } from "@/types";
import { Youtube, Search, Zap, FileText, ArrowRight, Sparkles, CheckCircle2, RefreshCw, AlertCircle, Play, Globe } from "lucide-react";

export default function OnboardingPage() {
  const router = useRouter();
  const { setActiveChannel } = useStore();

  const [step, setStep] = useState(1);
  const [creatorName, setCreatorName] = useState("");
  const [niche, setNiche] = useState("Tech & Programming");
  const [channelInput, setChannelInput] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState("");
  const [connectedChannel, setConnectedChannel] = useState<Channel | null>(null);

  // AI Sync stages
  const [stageProgress, setStageProgress] = useState([
    { id: 1, label: "Syncing YouTube API details & metadata...", status: "pending" },
    { id: 2, label: "Fetching latest 50 video statistics...", status: "pending" },
    { id: 3, label: "Extracting transcripts for top-performing content...", status: "pending" },
    { id: 4, label: "Building creator style profile & speaking voice...", status: "pending" },
    { id: 5, label: "Running competitor video gap detection...", status: "pending" },
    { id: 6, label: "Harvesting rising niche trends...", status: "pending" }
  ]);

  // Stage timer simulation while polling
  useEffect(() => {
    if (step !== 3 || !connectedChannel) return;

    let activeStage = 1;
    const interval = setInterval(async () => {
      try {
        // Poll backend channel status
        const response = await channelsApi.list();
        const updated = response.data.find((c: Channel) => c.id === connectedChannel.id);

        if (updated) {
          if (updated.analysis_status === "done") {
            clearInterval(interval);
            setStageProgress((prev) =>
              prev.map((s) => ({ ...s, status: "success" }))
            );
            setActiveChannel(updated);
            setTimeout(() => {
              setStep(4);
            }, 1000);
            return;
          } else if (updated.analysis_status === "failed") {
            clearInterval(interval);
            setError("Analysis failed but your channel was successfully connected. You can re-run analysis in the dashboard.");
            setTimeout(() => {
              setActiveChannel(updated);
              setStep(4);
            }, 2500);
            return;
          }
        }
      } catch (err) {
        console.error("Polling status error:", err);
      }

      // Simulate stage completions progressively while polling is still running
      setStageProgress((prev) =>
        prev.map((s) => {
          if (s.id < activeStage) return { ...s, status: "success" };
          if (s.id === activeStage) return { ...s, status: "loading" };
          return s;
        })
      );
      
      if (activeStage < 6) {
        activeStage += 1;
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [step, connectedChannel]);

  async function handleConnectChannel(e: React.FormEvent) {
    e.preventDefault();
    if (!channelInput.trim()) return;

    setConnecting(true);
    setError("");
    try {
      const resp = await channelsApi.connect(channelInput);
      setConnectedChannel(resp.data);
      setStep(3);
    } catch (err: any) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        "Failed to connect channel. Verify your Channel ID starts with 'UC' and try again."
      );
    } finally {
      setConnecting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex flex-col justify-between p-6 relative overflow-hidden">
      {/* Decorative Orbs */}
      <div className="absolute top-0 right-10 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[450px] h-[450px] bg-accent-purple/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Top Navbar */}
      <div className="max-w-4xl w-full mx-auto flex items-center justify-between border-b border-surface-border/50 pb-4 z-10">
        <span className="text-xl font-bold bg-gradient-brand bg-clip-text text-transparent">
          CreatorIQ
        </span>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className={step >= 1 ? "text-brand-400 font-semibold" : ""}>Profile</span>
          <span>/</span>
          <span className={step >= 2 ? "text-brand-400 font-semibold" : ""}>Channel</span>
          <span>/</span>
          <span className={step >= 3 ? "text-brand-400 font-semibold" : ""}>AI Processing</span>
          <span>/</span>
          <span className={step >= 4 ? "text-brand-400 font-semibold" : ""}>Done</span>
        </div>
      </div>

      {/* Main Wizard Card */}
      <div className="flex-1 flex items-center justify-center max-w-xl w-full mx-auto py-12 z-10">
        {step === 1 && (
          <div className="bg-surface-card border border-surface-border rounded-2xl p-8 shadow-2xl space-y-6 w-full backdrop-blur-sm">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" /> Step 1 of 3
              </div>
              <h2 className="text-2xl font-bold">Welcome to CreatorIQ!</h2>
              <p className="text-gray-400 text-xs leading-relaxed">
                Let's configure your AI niche settings so our intelligence scrapers scan the correct communities.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 block mb-1.5">Creator or Brand Name</label>
                <input
                  type="text"
                  value={creatorName}
                  onChange={(e) => setCreatorName(e.target.value)}
                  placeholder="e.g. CodeBuddy"
                  className="w-full bg-surface border border-surface-border rounded-lg px-3.5 py-2.5 text-white text-sm focus:outline-none focus:border-brand-500 transition"
                />
              </div>

              <div>
                <label className="text-xs text-gray-400 block mb-1.5">Primary Content Category</label>
                <select
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  className="w-full bg-surface border border-surface-border rounded-lg px-3.5 py-2.5 text-white text-sm focus:outline-none focus:border-brand-500 transition"
                >
                  <option>Tech & Programming</option>
                  <option>Gaming & Entertainment</option>
                  <option>Business & Finance</option>
                  <option>Education & Science</option>
                  <option>Lifestyle & Vlogs</option>
                  <option>Fitness & Health</option>
                </select>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!creatorName.trim()}
              className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition flex items-center justify-center gap-2"
            >
              Continue <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="bg-surface-card border border-surface-border rounded-2xl p-8 shadow-2xl space-y-6 w-full backdrop-blur-sm">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" /> Step 2 of 3
              </div>
              <h2 className="text-2xl font-bold">Connect your YouTube Channel</h2>
              <p className="text-gray-400 text-xs leading-relaxed">
                Connect your channel so our models fetch your latest video statistics and speaking profile.
              </p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleConnectChannel} className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 block mb-1.5">YouTube Channel ID or Handle</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={channelInput}
                    onChange={(e) => setChannelInput(e.target.value)}
                    placeholder="UC... or @handle"
                    required
                    className="flex-1 bg-surface border border-surface-border rounded-lg px-3.5 py-2.5 text-white text-sm focus:outline-none focus:border-brand-500 transition"
                  />
                </div>
                <span className="text-[10px] text-gray-500 mt-2 block">
                  Find your channel ID starting with "UC" in your Advanced Account Settings URL.
                </span>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 bg-surface border border-surface-border hover:bg-[#1e293b]/70 text-gray-300 font-medium py-2.5 rounded-lg transition text-sm"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={connecting || !channelInput.trim()}
                  className="flex-1 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition flex items-center justify-center gap-2 text-sm"
                >
                  {connecting ? "Connecting..." : "Synchronize Channel"}
                </button>
              </div>
            </form>
          </div>
        )}

        {step === 3 && (
          <div className="bg-surface-card border border-surface-border rounded-2xl p-8 shadow-2xl space-y-6 w-full backdrop-blur-sm text-center">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative">
                <div className="absolute inset-0 bg-brand-500/20 rounded-full blur-md animate-pulse" />
                <div className="w-16 h-16 rounded-full bg-brand-600/10 border border-brand-500/30 flex items-center justify-center">
                  <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
                </div>
              </div>
              <div className="space-y-1">
                <h2 className="text-xl font-bold bg-gradient-brand bg-clip-text text-transparent">
                  Syncing & Analyzing Channel Context
                </h2>
                <p className="text-xs text-gray-500 max-w-sm mx-auto">
                  Our background intelligence processes are compiling your content statistics, styles, and niche gaps. This takes about 1-2 minutes.
                </p>
              </div>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-xs flex items-center justify-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}

            {/* Sync Stage Progression list */}
            <div className="border border-surface-border/50 rounded-xl p-4 bg-surface/50 text-left space-y-3 max-h-[220px] overflow-y-auto">
              {stageProgress.map((s) => (
                <div key={s.id} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    {s.status === "success" && (
                      <CheckCircle2 className="w-4 h-4 text-accent-green flex-shrink-0" />
                    )}
                    {s.status === "loading" && (
                      <RefreshCw className="w-4 h-4 text-brand-400 animate-spin flex-shrink-0" />
                    )}
                    {s.status === "pending" && (
                      <div className="w-4 h-4 rounded-full border border-gray-700 flex-shrink-0" />
                    )}
                    <span className={s.status === "success" ? "text-gray-300" : s.status === "loading" ? "text-white font-medium" : "text-gray-500"}>
                      {s.label}
                    </span>
                  </div>
                  {s.status === "success" && (
                    <span className="text-[10px] text-accent-green font-semibold bg-accent-green/10 px-2 py-0.5 rounded-full">
                      Done
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="bg-surface-card border border-surface-border rounded-2xl p-8 shadow-2xl space-y-6 w-full backdrop-blur-sm text-center">
            <div className="flex flex-col items-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-accent-green/10 border border-accent-green/30 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-accent-green" />
              </div>
              <div className="space-y-1">
                <h2 className="text-2xl font-bold text-white">Creator Engine Ready!</h2>
                <p className="text-xs text-gray-400 max-w-sm mx-auto">
                  Your YouTube channel has been fully analyzed. Style profiles, competitor gap metrics, and niche trends are permanently saved in our databases.
                </p>
              </div>
            </div>

            {/* Premium Stat cards */}
            <div className="grid grid-cols-2 gap-4 border border-surface-border/50 rounded-xl p-4 bg-surface/50 text-left">
              <div>
                <p className="text-gray-500 text-[10px]">Connected Channel</p>
                <p className="text-white text-xs font-bold truncate mt-0.5">
                  {connectedChannel?.title || creatorName}
                </p>
              </div>
              <div>
                <p className="text-gray-500 text-[10px]">Growth Category</p>
                <p className="text-brand-400 text-xs font-bold mt-0.5">
                  {connectedChannel?.niche || niche}
                </p>
              </div>
            </div>

            <button
              onClick={() => router.push("/dashboard")}
              className="w-full bg-gradient-brand hover:opacity-95 text-white font-semibold py-3 rounded-xl transition shadow-xl shadow-brand-500/10 flex items-center justify-center gap-2"
            >
              Enter Growth Dashboard <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="max-w-4xl w-full mx-auto text-center text-xs text-gray-600 border-t border-surface-border/50 pt-4 z-10">
        © 2026 CreatorIQ. Secure SSL Data Connection.
      </div>
    </div>
  );
}
