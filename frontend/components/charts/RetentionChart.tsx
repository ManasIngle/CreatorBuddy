"use client";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface RetentionChartProps {
  data: { time: string; retention: number }[];
  className?: string;
}

export function RetentionChart({ data, className }: RetentionChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200} className={className}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="retentionGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
        <XAxis
          dataKey="time"
          stroke="#9ca3af"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#9ca3af"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          domain={[0, 100]}
          tickFormatter={(v) => `${v}%`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
          labelStyle={{ color: "#9ca3af" }}
          formatter={(value: number) => [`${value.toFixed(1)}%`, "Retention"]}
        />
        <Area
          type="monotone"
          dataKey="retention"
          stroke="#6366f1"
          strokeWidth={2}
          fill="url(#retentionGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function RetentionSkeleton() {
  return (
    <div className="w-full h-[200px] bg-surface-card rounded-xl animate-pulse" />
  );
}

export function RetentionEmpty() {
  return (
    <div className="w-full h-[200px] bg-surface-card rounded-xl flex items-center justify-center">
      <p className="text-gray-500 text-sm">No retention data available</p>
    </div>
  );
}