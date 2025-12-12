"use client";
import { useState, useEffect } from "react";
import { competitorsApi, channelsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { CompetitorCard, CompetitorCardSkeleton, CompetitorCardEmpty } from "@/components/intelligence/CompetitorCard";
import { Plus, TrendingUp, Search, AlertCircle, Users } from "lucide-react";
import type { Competitor } from "@/types";

export default function CompetitorsPage() {
  const { activeChannel } = useStore();
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newChannelId, setNewChannelId] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCompetitors() {
      if (!activeChannel) {
        setLoading(false);
        return;
      }
      try {
        const response = await competitorsApi.list(activeChannel.id);
        setCompetitors(response.data);
      } catch (e) {
        console.error("Failed to load competitors", e);
      } finally {
        setLoading(false);
      }
    }
    loadCompetitors();
  }, [activeChannel]);

  const handleAddCompetitor = async () => {
    if (!activeChannel || !newChannelId.trim()) return;
    setAdding(true);
    setError(null);
    try {
      await competitorsApi.add(activeChannel.id, newChannelId.trim());
      const response = await competitorsApi.list(activeChannel.id);
      setCompetitors(response.data);
      setShowAddModal(false);
      setNewChannelId("");
    } catch (e: any) {
      setError(e.response?.data?.detail || "Failed to add competitor");
    } finally {
      setAdding(false);
    }
  };

  const stats = {
    total: competitors.length,
    totalSubs: competitors.reduce((sum, c) => sum + c.subscriber_count, 0),
    avgOverlap: competitors.length > 0
      ? (competitors.reduce((sum, c) => sum + c.niche_overlap_score, 0) / competitors.length * 100).toFixed(0)
      : 0,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Competitor Analysis</h1>
          <p className="text-gray-400 text-sm mt-1">
            Track and learn from your competitors
          </p>
        </div>
        <Button
          onClick={() => setShowAddModal(true)}
          disabled={!activeChannel}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Competitor
        </Button>
      </div>

      {/* Stats */}
      {competitors.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-brand-400" />
              <div>
                <p className="text-white text-xl font-bold">{stats.total}</p>
                <p className="text-gray-500 text-xs">Competitors</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-accent-purple" />
              <div>
                <p className="text-white text-xl font-bold">{stats.totalSubs.toLocaleString()}</p>
                <p className="text-gray-500 text-xs">Total Subscribers</p>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-accent-green" />
              <div>
                <p className="text-white text-xl font-bold">{stats.avgOverlap}%</p>
                <p className="text-gray-500 text-xs">Avg Niche Overlap</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Competitor List */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <CompetitorCardSkeleton key={i} />
          ))}
        </div>
      ) : competitors.length === 0 ? (
        <CompetitorCardEmpty />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {competitors.map((competitor) => (
            <CompetitorCard
              key={competitor.id}
              competitor={competitor}
              channelId={activeChannel!.id}
            />
          ))}
        </div>
      )}

      {/* Add Competitor Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Competitor"
      >
        <div className="space-y-4">
          <div>
            <label className="text-white text-sm font-medium block mb-2">
              YouTube Channel ID or Handle
            </label>
            <Input
              value={newChannelId}
              onChange={(e) => setNewChannelId(e.target.value)}
              placeholder="e.g., @channelname or UC..."
            />
            <p className="text-gray-500 text-xs mt-1">
              Enter the channel ID (UC...) or @handle
            </p>
          </div>
          {error && (
            <p className="text-accent-red text-sm">{error}</p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddCompetitor} disabled={adding || !newChannelId.trim()}>
              {adding ? "Adding..." : "Add Competitor"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}