import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Dev-only proxy so relative /api/* calls can reach the local backend.
    // Production uses NEXT_PUBLIC_API_BASE_URL via frontend/lib/api-base.ts.
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    const backend =
      process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
      process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
      "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
