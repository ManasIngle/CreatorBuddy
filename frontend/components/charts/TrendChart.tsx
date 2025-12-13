"use client";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface TrendData {
  topic: string;
  velocity: number;
  saturation: number;
  opportunity: number;
}

interface TrendChartProps {
  data: TrendData[];
  className?: string;
}

export function TrendChart({ data, className }: TrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280} className={className}>
      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="topic"
          tick={{ fill: "#9ca3af", fontSize: 11 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 10]}
          tick={{ fill: "#9ca3af", fontSize: 10 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
          labelStyle={{ color: "#9ca3af" }}
        />
        <Radar
          name="Velocity"
          dataKey="velocity"
          stroke="#6366f1"
          fill="#6366f1"
          fillOpacity={0.4}
        />
        <Radar
          name="Saturation"
          dataKey="saturation"
          stroke="#f59e0b"
          fill="#f59e0b"
          fillOpacity={0.2}
        />
        <Radar
          name="Opportunity"
          dataKey="opportunity"
          stroke="#22c55e"
          fill="#22c55e"
          fillOpacity={0.2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

export function TrendVelocityBar({ velocity }: { velocity: number }) {
  const bars = Array.from({ length: 10 }, (_, i) => i < Math.round(velocity));
  
  return (
    <div className="flex items-center gap-1">
      {bars.map((filled, i) => (
        <div
          key={i}
          className={`w-2 h-4 rounded-sm ${
            filled
              ? velocity >= 7
                ? "bg-accent-green"
                : velocity >= 4
                ? "bg-accent-yellow"
                : "bg-accent-orange"
              : "bg-surface-border"
          }`}
        />
      ))}
      <span className="ml-2 text-xs text-gray-400">{velocity.toFixed(1)}/10</span>
    </div>
  );
}

export function TrendSkeleton() {
  return <div className="w-full h-[280px] bg-surface-card rounded-xl animate-pulse" />;
}

export function TrendEmpty() {
  return (
    <div className="w-full h-[280px] bg-surface-card rounded-xl flex items-center justify-center">
      <p className="text-gray-500 text-sm">No trend data available</p>
    </div>
  );
}