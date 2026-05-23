"use client";
import { useState, useEffect } from "react";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Tabs } from "@/components/ui/Tabs";
import { Badge } from "@/components/ui/Badge";
import { Avatar } from "@/components/ui/Avatar";
import { Modal } from "@/components/ui/Modal";
import { authApi } from "@/lib/api";
import {
  User, Key, Bell, Palette, Users, CreditCard, Shield,
  ExternalLink, Check, AlertCircle, Trash2, Zap, Star, Sparkles
} from "lucide-react";

export default function SettingsPage() {
  const { activeChannel, user, setUser } = useStore();
  const [activeTab, setActiveTab] = useState("account");
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("upgrade") === "true") {
        setShowUpgradeModal(true);
        // Clear param from URL without reload
        const newUrl = window.location.pathname;
        window.history.replaceState({}, "", newUrl);
      }
    }
  }, []);

  const handleUpgrade = async (planId: string) => {
    setUpgrading(planId);
    setSuccessMessage("");
    try {
      const response = await authApi.updatePlan(planId);
      setUser(response.data);
      setSuccessMessage(`Successfully upgraded to the ${planId.toUpperCase()} plan!`);
      setShowUpgradeModal(false);
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (err: any) {
      console.error(err);
    } finally {
      setUpgrading(null);
    }
  };

  const planInfo = {
    free: { name: "Free", price: "$0/month", desc: "1 channel connected · 3 scripts/mo · 3 competitors" },
    starter: { name: "Starter", price: "$19/month", desc: "1 channel connected · 15 scripts/mo · 5 competitors" },
    pro: { name: "Pro", price: "$49/month", desc: "5 channels connected · Unlimited scripts · 10 competitors" },
    agency: { name: "Agency", price: "$149/month", desc: "25 channels connected · Unlimited scripts · 25 competitors" },
  };

  const currentPlan = user?.plan || "free";
  const planDetails = planInfo[currentPlan as keyof typeof planInfo] || planInfo.free;

  const pricingPlans = [
    {
      id: "free",
      name: "Free",
      price: "$0",
      desc: "For creators starting out",
      features: [
        "1 Connected Channel",
        "3 AI Scripts / month",
        "3 Competitors tracked",
        "100k Monthly Token Budget",
        "Standard intelligence",
      ],
      icon: User,
      color: "text-gray-400 border-gray-700/50 bg-gray-950/20",
    },
    {
      id: "starter",
      name: "Starter",
      price: "$19",
      desc: "For growing creators",
      features: [
        "1 Connected Channel",
        "15 AI Scripts / month",
        "5 Competitors tracked",
        "500k Monthly Token Budget",
        "Advanced intelligence",
      ],
      icon: Sparkles,
      color: "text-brand-400 border-brand-800/40 bg-brand-950/10",
    },
    {
      id: "pro",
      name: "Pro",
      price: "$49",
      desc: "Our most popular tier",
      features: [
        "5 Connected Channels",
        "Unlimited AI Scripts",
        "10 Competitors tracked",
        "2M Monthly Token Budget",
        "Real-time gap detection",
        "Priority AI analysis",
      ],
      icon: Zap,
      color: "text-indigo-400 border-indigo-800/40 bg-indigo-950/10",
      popular: true,
    },
    {
      id: "agency",
      name: "Agency",
      price: "$149",
      desc: "For production teams",
      features: [
        "25 Connected Channels",
        "Unlimited AI Scripts",
        "25 Competitors tracked",
        "10M Monthly Token Budget",
        "All features unlocked",
        "24/7 dedicated support",
      ],
      icon: Star,
      color: "text-accent-yellow border-accent-yellow/30 bg-accent-yellow/5",
    },
  ];

  return (
    <div className="space-y-6">
      {successMessage && (
        <div className="bg-accent-green/10 border border-accent-green/20 rounded-xl p-4 flex items-center gap-3 text-accent-green text-sm animate-pulse">
          <Check className="w-5 h-5 flex-shrink-0" />
          <span className="font-medium">{successMessage}</span>
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 text-sm mt-1">
          Manage your account and integrations
        </p>
      </div>

      <Tabs
        tabs={[
          { key: "account", label: "Account" },
          { key: "integrations", label: "Integrations" },
          { key: "notifications", label: "Notifications" },
        ]}
        activeTab={activeTab}
        onChange={(id) => setActiveTab(id as "account" | "integrations" | "notifications")}
      />

      {activeTab === "account" && (
        <div className="space-y-6">
          {/* Profile */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-medium">Profile</h3>
            </div>
            <div className="flex items-start gap-6">
              <Avatar
                src={activeChannel?.thumbnail_url || null}
                alt={activeChannel?.title || "User"}
                size="xl"
              />
              <div className="flex-1 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-400 text-xs block mb-1">Display Name</label>
                    <Input defaultValue={activeChannel?.title || ""} />
                  </div>
                  <div>
                    <label className="text-gray-400 text-xs block mb-1">Email</label>
                    <Input defaultValue="creator@example.com" type="email" />
                  </div>
                </div>
                <div>
                  <label className="text-gray-400 text-xs block mb-1">Bio</label>
                  <textarea
                    className="w-full bg-surface-elevated border border-surface-border rounded-lg px-3 py-2 text-sm text-white"
                    rows={3}
                    placeholder="Tell us about your channel..."
                  />
                </div>
                <Button>Save Changes</Button>
              </div>
            </div>
          </Card>

          {/* Password */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Key className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-medium">Password</h3>
            </div>
            <div className="space-y-4 max-w-md">
              <div>
                <label className="text-gray-400 text-xs block mb-1">Current Password</label>
                <Input type="password" />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">New Password</label>
                <Input type="password" />
              </div>
              <div>
                <label className="text-gray-400 text-xs block mb-1">Confirm New Password</label>
                <Input type="password" />
              </div>
              <Button>Update Password</Button>
            </div>
          </Card>

          {/* Plan */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <CreditCard className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-medium">Subscription Plan</h3>
            </div>
            <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-lg">
              <div>
                <div className="flex items-center gap-2">
                  <Badge variant="success" className="capitalize">{currentPlan}</Badge>
                  <span className="text-white font-medium">{planDetails.price}</span>
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  {planDetails.desc}
                </p>
              </div>
              <Button variant="ghost" onClick={() => setShowUpgradeModal(true)}>Manage Plan</Button>
            </div>
          </Card>

          {/* Upgrade Subscription Modal */}
          <Modal
            isOpen={showUpgradeModal}
            onClose={() => setShowUpgradeModal(false)}
            title="Upgrade Subscription Plan"
          >
            <div className="space-y-4 max-h-[85vh] overflow-y-auto pr-1">
              <p className="text-gray-400 text-sm">
                Scale your channel growth with one of our premium tiers. Choose the plan that best fits your workflow.
              </p>

              <div className="grid grid-cols-1 gap-4">
                {pricingPlans.map((plan) => {
                  const Icon = plan.icon;
                  const isActive = currentPlan === plan.id;
                  
                  return (
                    <div
                      key={plan.id}
                      className={`relative p-5 rounded-2xl border transition-all duration-300 ${
                        isActive
                          ? "border-brand-500 bg-brand-500/10 shadow-lg shadow-brand-500/10"
                          : plan.popular
                          ? "border-indigo-500/50 hover:border-indigo-400 bg-surface-elevated"
                          : "border-surface-border hover:border-gray-700 bg-surface-elevated"
                      }`}
                    >
                      {plan.popular && (
                        <span className="absolute top-3 right-3 text-[10px] bg-indigo-600 text-white font-bold px-2 py-0.5 rounded-full shadow">
                          POPULAR
                        </span>
                      )}

                      <div className="flex items-start gap-4">
                        <div className={`p-2.5 rounded-xl border ${plan.color}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        
                        <div className="flex-1 space-y-1">
                          <div className="flex items-baseline justify-between">
                            <h4 className="text-white font-semibold flex items-center gap-2 text-base">
                              {plan.name}
                              {isActive && (
                                <Badge variant="success" className="text-[10px] px-1.5 py-0.5">Active</Badge>
                              )}
                            </h4>
                            <div className="text-right">
                              <span className="text-white font-bold text-xl">{plan.price}</span>
                              <span className="text-gray-500 text-xs">/mo</span>
                            </div>
                          </div>
                          <p className="text-gray-400 text-xs leading-relaxed">{plan.desc}</p>
                        </div>
                      </div>

                      <div className="mt-4 pt-4 border-t border-surface-border flex items-center justify-between gap-4">
                        <ul className="grid grid-cols-2 gap-x-4 gap-y-1 flex-1">
                          {plan.features.slice(0, 4).map((feature) => (
                            <li key={feature} className="text-[11px] text-gray-500 flex items-center gap-1.5">
                              <Check className="w-3 h-3 text-brand-400 flex-shrink-0" />
                              <span className="truncate">{feature}</span>
                            </li>
                          ))}
                        </ul>

                        <Button
                          variant={isActive ? "outline" : plan.popular ? "default" : "ghost"}
                          disabled={isActive || upgrading !== null}
                          size="sm"
                          onClick={() => handleUpgrade(plan.id)}
                          className="flex-shrink-0 hover:scale-[1.03] active:scale-[0.97] transition-all"
                        >
                          {upgrading === plan.id ? (
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          ) : isActive ? (
                            "Current Plan"
                          ) : (
                            "Select"
                          )}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="flex justify-end pt-2 border-t border-surface-border">
                <Button variant="ghost" onClick={() => setShowUpgradeModal(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </Modal>

          {/* Danger Zone */}
          <Card className="p-5 border-accent-red/30">
            <div className="flex items-center gap-2 mb-4">
              <AlertCircle className="w-4 h-4 text-accent-red" />
              <h3 className="text-white font-medium">Danger Zone</h3>
            </div>
            <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-lg">
              <div>
                <p className="text-white text-sm font-medium">Delete Account</p>
                <p className="text-gray-400 text-xs">
                  Permanently delete your account and all data
                </p>
              </div>
              <Button variant="ghost" className="text-accent-red hover:text-accent-red">
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </Button>
            </div>
          </Card>
        </div>
      )}

      {activeTab === "integrations" && (
        <div className="space-y-6">
          {/* YouTube Connection */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-4 h-4 text-accent-red" />
              <h3 className="text-white font-medium">YouTube Connection</h3>
            </div>
            {activeChannel ? (
              <div className="flex items-center justify-between p-4 bg-surface-elevated rounded-lg">
                <div className="flex items-center gap-3">
                  <img
                    src={activeChannel.thumbnail_url || ""}
                    alt={activeChannel.title}
                    className="w-10 h-10 rounded-full"
                  />
                  <div>
                    <p className="text-white text-sm font-medium">{activeChannel.title}</p>
                    <p className="text-gray-400 text-xs">
                      {activeChannel.subscriber_count.toLocaleString()} subscribers
                    </p>
                  </div>
                </div>
                <Badge variant="green">
                  <Check className="w-3 h-3 mr-1" />
                  Connected
                </Badge>
              </div>
            ) : (
              <div className="p-4 bg-surface-elevated rounded-lg text-center">
                <p className="text-gray-400 text-sm">No YouTube channel connected</p>
                <Button className="mt-3" asChild>
                  <a href="/channel">Connect Channel</a>
                </Button>
              </div>
            )}
          </Card>

          {/* API Access */}
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Key className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-medium">API Access</h3>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Use API keys to integrate CreatorIQ with your own applications.
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg">
                <span className="text-gray-300 text-sm">API Key</span>
                <Button variant="ghost" size="sm">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Generate
                </Button>
              </div>
            </div>
          </Card>

          {/* Integrations */}
          <Card className="p-5">
            <h3 className="text-white font-medium mb-4">Third-Party Integrations</h3>
            <div className="space-y-3">
              {[
                { name: "Zapier", desc: "Connect with 5000+ apps", connected: false },
                { name: "Make (Integromat)", desc: "Automate workflows", connected: false },
                { name: "Pabbly", desc: "API integration platform", connected: false },
              ].map((integration) => (
                <div
                  key={integration.name}
                  className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg"
                >
                  <div>
                    <p className="text-white text-sm font-medium">{integration.name}</p>
                    <p className="text-gray-500 text-xs">{integration.desc}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Connect
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {activeTab === "notifications" && (
        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Bell className="w-4 h-4 text-brand-400" />
              <h3 className="text-white font-medium">Email Notifications</h3>
            </div>
            <div className="space-y-4">
              {[
                { label: "Trend alerts", desc: "When new trending topics match your niche", enabled: true },
                { label: "Competitor updates", desc: "When competitors upload new videos", enabled: true },
                { label: "Weekly digest", desc: "Summary of your channel performance", enabled: false },
                { label: "Script generation complete", desc: "When AI script is ready", enabled: true },
              ].map((notification) => (
                <div
                  key={notification.label}
                  className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg"
                >
                  <div>
                    <p className="text-white text-sm font-medium">{notification.label}</p>
                    <p className="text-gray-500 text-xs">{notification.desc}</p>
                  </div>
                  <button
                    className={`w-10 h-6 rounded-full transition ${
                      notification.enabled ? "bg-brand-600" : "bg-gray-600"
                    }`}
                  >
                    <div
                      className={`w-4 h-4 bg-white rounded-full transition transform ${
                        notification.enabled ? "translate-x-5" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="text-white font-medium mb-4">Browser Notifications</h3>
            <p className="text-gray-400 text-sm mb-4">
              Receive push notifications when you're not on the site.
            </p>
            <Button variant="outline">Enable Browser Notifications</Button>
          </Card>
        </div>
      )}
    </div>
  );
}