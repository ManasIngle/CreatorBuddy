import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  
  // Compression is handled by the backend GZipMiddleware
  // But we can add brotli compression for static assets
  
  // Build optimizations
  swcMinify: true,
  
  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.ytimg.com',
      },
      {
        protocol: 'https',
        hostname: '**.googleusercontent.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days for YouTube thumbnails
  },
  
  // Headers for caching and security
  async headers() {
    return [
      {
        source: '/sw.js',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400, stale-while-revalidate=604800',
          },
        ],
      },
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400',
          },
        ],
      },
      {
        source: '/(.*)\\.(ico|png|svg|jpg|jpeg|gif|webp|avif)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  
  // Experimental features
  experimental: {
    // Enable optimized package imports
    optimizePackageImports: ['@tanstack/react-query', 'lucide-react', 'clsx'],
  },
};

export default nextConfig;