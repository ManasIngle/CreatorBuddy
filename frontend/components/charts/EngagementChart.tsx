"use client";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface EngagementData {
  date: string;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
}

interface EngagementChartProps {
  data: EngagementData[];
  type?: "bar" | "line";
  className?: string;
}

export function EngagementChart({ data, type = "bar", className }: EngagementChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    engagement_pct: (d.engagement_rate * 100).toFixed(1),
  }));

  if (type === "line") {
    return (
      <ResponsiveContainer width="100%" height={200} className={className}>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis
            dataKey="date"
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
          <Legend wrapperStyle={{ fontSize: 12, color: "#9ca3af" }} />
          <Line
            type="monotone"
            dataKey="likes"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            name="Likes"
          />
          <Line
            type="monotone"
            dataKey="comments"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
            name="Comments"
          />
          <Line
            type="monotone"
            dataKey="shares"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
            name="Shares"
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200} className={className}>
      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
        <XAxis
          dataKey="date"
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
        <Legend wrapperStyle={{ fontSize: 12, color: "#9ca3af" }} />
        <Bar dataKey="likes" fill="#6366f1" radius={[4, 4, 0, 0]} name="Likes" />
        <Bar dataKey="comments" fill="#22c55e" radius={[4, 4, 0, 0]} name="Comments" />
        <Bar dataKey="shares" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Shares" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function EngagementSkeleton() {
  return <div className="w-full h-[200px] bg-surface-card rounded-xl animate-pulse" />;
}

export function EngagementEmpty() {
  return (
    <div className="w-full h-[200px] bg-surface-card rounded-xl flex items-center justify-center">
      <p className="text-gray-500 text-sm">No engagement data available</p>
    </div>
  );
}