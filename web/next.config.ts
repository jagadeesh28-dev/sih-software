import type { NextConfig } from "next";

// All scientific data comes from the Python API (api/main.py); the frontend only proxies to it.
const API_ORIGIN = process.env.EQ_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/api/:path*` }];
  },
};

export default nextConfig;
