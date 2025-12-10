import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
        surface: {
          DEFAULT: "#0f172a",
          card: "#1e293b",
          border: "#334155",
          muted: "#475569",
        },
        accent: {
          green: "#22c55e",
          orange: "#f97316",
          purple: "#a855f7",
          red: "#ef4444",
          yellow: "#eab308",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "gradient-brand": "linear-gradient(135deg, #0ea5e9 0%, #a855f7 100%)",
        "gradient-card": "linear-gradient(145deg, #1e293b 0%, #0f172a 100%)",
      },
    },
  },
  plugins: [],
};

export default config;