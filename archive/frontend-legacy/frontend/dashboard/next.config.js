/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  env: {
    API_URL: process.env.API_URL || "http://localhost:8080",
    WS_URL: process.env.WS_URL || "ws://localhost:8081",
  },
};

module.exports = nextConfig;
