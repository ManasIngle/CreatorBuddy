"use client";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface GrowthData {
  date: string;
  subscribers: number;
  views: number;
  videos: number;
}

interface GrowthChartProps {
  data: GrowthData[];
  metric?: "subscribers" | "views" | "all";
  className?: string;
}

export function GrowthChart({ data, metric = "all", className }: GrowthChartProps) {
  if (metric === "subscribers") {
    return (
      <ResponsiveContainer width="100%" height={200} className={className}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="subGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
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
            tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1f2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#f9fafb",
            }}
            labelStyle={{ color: "#9ca3af" }}
            formatter={(value: number) => [value.toLocaleString(), "Subscribers"]}
          />
          <Area
            type="monotone"
            dataKey="subscribers"
            stroke="#8b5cf6"
            strokeWidth={2}
            fill="url(#subGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  if (metric === "views") {
    return (
      <ResponsiveContainer width="100%" height={200} className={className}>
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
            tickFormatter={(v) => v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1f2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#f9fafb",
            }}
            labelStyle={{ color: "#9ca3af" }}
            formatter={(value: number) => [value.toLocaleString(), "Views"]}
          />
          <Line
            type="monotone"
            dataKey="views"
            stroke="#06b6d4"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200} className={className}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
          tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
          labelStyle={{ color: "#9ca3af" }}
          formatter={(value: number, name: string) => [
            value.toLocaleString(),
            name === "subscribers" ? "Subscribers" : name === "views" ? "Views" : "Videos"
          ]}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#9ca3af" }} />
        <Line
          type="monotone"
          dataKey="subscribers"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={false}
          name="Subscribers"
        />
        <Line
          type="monotone"
          dataKey="views"
          stroke="#06b6d4"
          strokeWidth={2}
          dot={false}
          name="Views"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function GrowthSkeleton() {
  return <div className="w-full h-[200px] bg-surface-card rounded-xl animate-pulse" />;
}

export function GrowthEmpty() {
  return (
    <div className="w-full h-[200px] bg-surface-card rounded-xl flex items-center justify-center">
      <p className="text-gray-500 text-sm">No growth data available</p>
    </div>
  );
}