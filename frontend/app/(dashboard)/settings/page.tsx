"use client";
import { useState } from "react";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Tabs } from "@/components/ui/Tabs";
import { Badge } from "@/components/ui/Badge";
import { Avatar } from "@/components/ui/Avatar";
import {
  User, Key, Bell, Palette, Users, CreditCard, Shield,
  ExternalLink, Check, AlertCircle, Trash2
} from "lucide-react";

export default function SettingsPage() {
  const { activeChannel } = useStore();
  const [activeTab, setActiveTab] = useState("account");

  return (
    <div className="space-y-6">
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
                  <Badge variant="brand">Pro</Badge>
                  <span className="text-white font-medium">$29/month</span>
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  Unlimited channels, AI analysis, competitor tracking
                </p>
              </div>
              <Button variant="ghost">Manage Plan</Button>
            </div>
          </Card>

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