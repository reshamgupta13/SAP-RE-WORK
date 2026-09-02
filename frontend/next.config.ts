import type { NextConfig } from "next";

function resolveBackendUrl(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
    process.env.API_BASE_URL?.replace(/\/+$/, "") ||
    (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "")
  );
}

const nextConfig: NextConfig = {
  async rewrites() {
    const backend = resolveBackendUrl();
    if (!backend) {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
