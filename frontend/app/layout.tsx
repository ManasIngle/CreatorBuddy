import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "CreatorIQ - AI Growth Intelligence for Creators",
    template: "%s | CreatorIQ",
  },
  description: "AI-powered YouTube growth intelligence platform. Get competitor analysis, content gap detection, viral hooks, and optimized scripts.",
  keywords: [
    "YouTube growth",
    "content creator tools",
    "YouTube analytics",
    "AI scripting",
    "video optimization",
    "creator economy",
    "content strategy",
    "YouTube SEO",
  ],
  authors: [{ name: "CreatorIQ" }],
  creator: "CreatorIQ",
  publisher: "CreatorIQ",
  manifest: "/manifest.json",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  twitter: {
    card: "summary_large_image",
    title: "CreatorIQ - AI Growth Intelligence for Creators",
    description: "AI-powered YouTube growth intelligence platform",
    creator: "@creatoriq",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://creatoriq.io",
    siteName: "CreatorIQ",
    title: "CreatorIQ - AI Growth Intelligence for Creators",
    description: "AI-powered YouTube growth intelligence platform. Get competitor analysis, content gap detection, viral hooks, and optimized scripts.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "CreatorIQ - AI Growth Intelligence",
      },
    ],
  },
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    apple: "/icons/icon-192x192.png",
    other: [
      {
        rel: "manifest",
        url: "/manifest.json",
      },
    ],
  },
  verification: {
    google: "google-site-verification-code",
  },
};

export const viewport: Viewport = {
  themeColor: "#6366f1",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}