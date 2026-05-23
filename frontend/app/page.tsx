"use client";
import Link from "next/link";
import { TrendingUp, Search, Zap, FileText, ArrowRight, Shield, Sparkles, BarChart2, Users } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0f172a] text-white selection:bg-brand-500/30 overflow-x-hidden">
      {/* Premium Gradient Background Orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-[20%] right-10 w-[600px] h-[600px] bg-accent-purple/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[450px] h-[450px] bg-accent-orange/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <header className="border-b border-surface-border/50 backdrop-blur-md sticky top-0 z-50 bg-[#0f172a]/70">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold bg-gradient-brand bg-clip-text text-transparent tracking-tight">
              CreatorIQ
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-300 font-medium">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#mockup" className="hover:text-white transition">Dashboard</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm text-gray-300 hover:text-white font-medium transition">
              Sign In
            </Link>
            <Link
              href="/register"
              className="bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition shadow-lg shadow-brand-600/25"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 md:pt-32 md:pb-24">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Introducing CreatorIQ 1.0
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold leading-[1.1] tracking-tight">
            The AI Copilot for <br className="hidden md:inline" />
            <span className="bg-gradient-brand bg-clip-text text-transparent">
              YouTube Channel Growth
            </span>
          </h1>
          <p className="text-gray-400 text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
            Stop guessing what content to make. Analyze competitor gaps, track rising niche trends, 
            optimize speaking styles, and draft viral scripts in seconds. Built for creators who want to scale.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href="/register"
              className="w-full sm:w-auto bg-gradient-brand hover:opacity-90 text-white font-semibold px-8 py-3.5 rounded-xl transition shadow-xl shadow-brand-500/20 flex items-center justify-center gap-2"
            >
              Start Growing Free <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#features"
              className="w-full sm:w-auto bg-surface-card border border-surface-border hover:bg-surface-card/80 text-gray-200 font-medium px-8 py-3.5 rounded-xl transition flex items-center justify-center"
            >
              Explore Features
            </a>
          </div>
        </div>
      </section>

      {/* Interactive Mockup Preview */}
      <section id="mockup" className="max-w-6xl mx-auto px-6 pb-24 relative">
        <div className="bg-gradient-card p-2 rounded-2xl border border-surface-border shadow-2xl relative overflow-hidden backdrop-blur-sm">
          <div className="border border-surface-border/50 rounded-xl overflow-hidden bg-[#0f172a]/90">
            {/* Window control dots */}
            <div className="h-10 bg-surface-card border-b border-surface-border/50 px-4 flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-accent-red/40" />
              <div className="w-3 h-3 rounded-full bg-accent-yellow/40" />
              <div className="w-3 h-3 rounded-full bg-accent-green/40" />
              <span className="text-xs text-gray-500 ml-4 font-mono">creatoriq.app/dashboard</span>
            </div>
            
            {/* Mockup Content Grid */}
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-surface-border/30 pb-4">
                <div>
                  <h3 className="font-bold text-white text-lg">Growth Dashboard</h3>
                  <p className="text-xs text-gray-400">AI analysis for Creator Niche Channel</p>
                </div>
                <div className="px-3 py-1 bg-accent-green/10 text-accent-green text-xs font-semibold rounded-full border border-accent-green/20">
                  Live Sync Active
                </div>
              </div>

              {/* Stats row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Subscribers", value: "348,200", change: "+12.4% MoM" },
                  { label: "Avg Video Views", value: "89,450", change: "Top 5% Niche" },
                  { label: "Content Gaps", value: "8 Detected", change: "High Opportunity" },
                  { label: "Niche Rating", value: "Tech & Coding", change: "High Growth" }
                ].map((s) => (
                  <div key={s.label} className="bg-surface-card/60 p-4 border border-surface-border/30 rounded-xl">
                    <p className="text-xs text-gray-400">{s.label}</p>
                    <p className="text-white text-lg font-bold mt-1">{s.value}</p>
                    <p className="text-[10px] text-brand-400 font-medium mt-0.5">{s.change}</p>
                  </div>
                ))}
              </div>

              {/* Feature Preview row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Gaps Mockup */}
                <div className="bg-[#1e293b]/40 border border-surface-border/40 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-accent-orange flex items-center gap-1.5">
                      <Search className="w-3.5 h-3.5" /> High-Value Content Gaps
                    </span>
                    <span className="text-[10px] text-gray-500">Updated 10m ago</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { topic: "Rust vs Go for Microservices in 2026", comp: "Low", rating: "9.4/10" },
                      { topic: "How I Built a SaaS in 24 Hours with Next.js 16", comp: "Medium", rating: "8.8/10" }
                    ].map((g) => (
                      <div key={g.topic} className="flex items-center justify-between p-2.5 rounded bg-surface-card/40 border border-surface-border/20 text-xs">
                        <span className="text-gray-200 font-medium">{g.topic}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-gray-400">Comp: {g.comp}</span>
                          <span className="text-accent-green font-bold">{g.rating}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Script Mockup */}
                <div className="bg-[#1e293b]/40 border border-surface-border/40 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-brand-400 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" /> AI Script Generator Draft
                    </span>
                    <span className="text-[10px] text-gray-500">Speaking Style: Engaging</span>
                  </div>
                  <div className="space-y-2 border border-surface-border/30 rounded-lg p-3 bg-surface-card/20 text-xs text-gray-400 h-[100px] overflow-hidden relative">
                    <p className="text-brand-300 font-bold mb-1">[0:00 - 0:30] Hook</p>
                    <p>"Most software developers fail to scale their products not because of clean code, but because they ignored this one metric..."</p>
                    <div className="absolute bottom-0 left-0 right-0 h-10 bg-gradient-to-t from-[#0f172a]/90 to-transparent" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-12 md:py-24 border-t border-surface-border/30">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl font-bold">Comprehensive Growth Engines</h2>
          <p className="text-gray-400 text-sm">
            CreatorIQ embeds intelligent AI models alongside real-time web scraping to extract content suggestions that make a difference.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: "Content Gap Engine",
              desc: "Scrapes competitor upload patterns and niche communities to reveal high-demand topics that have surprisingly low competition.",
              icon: Search,
              color: "text-accent-orange bg-accent-orange/10 border-accent-orange/20"
            },
            {
              title: "Viral Hook Intelligence",
              desc: "Analyzes the transcripts of top-performing videos in your field, crafting retention-optimized opening hooks and transition points.",
              icon: Zap,
              color: "text-accent-green bg-accent-green/10 border-accent-green/20"
            },
            {
              title: "Competitor Analysis",
              desc: "Keeps an automated eye on video metrics, tags, and speaking styles of top creators, keeping your strategy ahead of changes.",
              icon: TrendingUp,
              color: "text-accent-purple bg-accent-purple/10 border-accent-purple/20"
            },
            {
              title: "AI Script Editor",
              desc: "Drafts high-retention video outlines or full spoken scripts tailored specifically to your speaker profile and duration preferences.",
              icon: FileText,
              color: "text-brand-400 bg-brand-400/10 border-brand-400/20"
            },
            {
              title: "Trend Tracker",
              desc: "Aggregates breaking topics from Google Trends, Reddit discussions, and Quora threads in real-time before they saturate standard tools.",
              icon: BarChart2,
              color: "text-accent-yellow bg-accent-yellow/10 border-accent-yellow/20"
            },
            {
              title: "Audience Persona Extraction",
              desc: "Mines video comments and niche discussions to detail target demographic pain points, speaking angles, and immediate content desires.",
              icon: Users,
              color: "text-brand-200 bg-brand-200/10 border-brand-200/20"
            }
          ].map((f) => (
            <div key={f.title} className="bg-surface-card border border-surface-border rounded-2xl p-6 space-y-4 hover:border-brand-500/30 transition group">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${f.color}`}>
                <f.icon className="w-5 h-5" />
              </div>
              <h3 className="text-white font-bold text-base group-hover:text-brand-300 transition">{f.title}</h3>
              <p className="text-gray-400 text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Subscription Pricing Grid */}
      <section id="pricing" className="max-w-7xl mx-auto px-6 py-12 md:py-24 border-t border-surface-border/30">
        <div className="text-center max-w-2xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl font-bold">Flexible Plans for Every Creator</h2>
          <p className="text-gray-400 text-sm">
            Upgrade, downgrade, or cancel at any time. Start generating actionable content recommendations instantly.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {[
            {
              name: "Free",
              price: "$0",
              desc: "For exploring features",
              features: ["1 Connected Channel", "3 Competitors Tracked", "3 Scripts per Month", "Standard Token Allowance"],
              cta: "Start Free",
              popular: false
            },
            {
              name: "Starter",
              price: "$19",
              desc: "For serious solo creators",
              features: ["1 Connected Channel", "5 Competitors Tracked", "15 Scripts per Month", "Starter Token Allowance", "Priority Trend Tracking"],
              cta: "Upgrade to Starter",
              popular: false
            },
            {
              name: "Pro",
              price: "$49",
              desc: "For growing channels",
              features: ["5 Connected Channels", "10 Competitors Tracked", "Unlimited Script Drafts", "High Token Allowance", "Full Audience Psychology"],
              cta: "Upgrade to Pro",
              popular: true
            },
            {
              name: "Agency",
              price: "$149",
              desc: "For networks & managers",
              features: ["25 Connected Channels", "25 Competitors Tracked", "Unlimited Script Drafts", "Max Token Allowance", "Custom Brand Voice Style"],
              cta: "Upgrade to Agency",
              popular: false
            }
          ].map((plan) => (
            <div
              key={plan.name}
              className={`bg-surface-card rounded-2xl border p-6 flex flex-col justify-between hover:scale-[1.02] transition-transform ${
                plan.popular 
                  ? "border-brand-500 shadow-xl shadow-brand-500/10 relative" 
                  : "border-surface-border"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 right-4 bg-brand-600 text-white text-[10px] font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                  Most Popular
                </span>
              )}
              <div className="space-y-4">
                <div>
                  <h4 className="text-white font-bold text-lg">{plan.name}</h4>
                  <p className="text-gray-500 text-[11px] mt-0.5">{plan.desc}</p>
                </div>
                <div className="flex items-baseline gap-1 py-2">
                  <span className="text-3xl font-extrabold text-white">{plan.price}</span>
                  <span className="text-gray-500 text-xs">/mo</span>
                </div>
                <div className="flex-1 border-t border-surface-border/50 pt-4">
                  <ul className="space-y-2 text-xs text-gray-400">
                    {plan.features.map((feat) => (
                      <li key={feat} className="flex items-center gap-2">
                        <Shield className="w-3 h-3 text-brand-400 flex-shrink-0" />
                        <span className="truncate">{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="pt-6">
                <Link
                  href="/register"
                  className={`w-full text-center py-2 px-4 rounded-lg text-xs font-bold transition flex items-center justify-center ${
                    plan.popular
                      ? "bg-brand-600 text-white hover:bg-brand-700 shadow-md"
                      : "bg-[#1e293b] text-gray-200 hover:bg-[#1e293b]/70 border border-surface-border/85"
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-surface-border/40 py-12 bg-[#0f172a]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-gray-500">
          <p>© 2026 CreatorIQ. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a href="#" className="hover:text-gray-300">Privacy Policy</a>
            <a href="#" className="hover:text-gray-300">Terms of Service</a>
            <a href="#" className="hover:text-gray-300">Contact Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
