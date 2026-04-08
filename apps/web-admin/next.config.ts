import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Point Prisma to the web-client's shared SQLite db
  env: {
    DATABASE_URL: process.env.DATABASE_URL ?? "file:../web-client/prisma/dev.db",
  },
};

export default nextConfig;
