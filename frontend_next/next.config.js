/** @type {import('next').NextConfig} */
const nextConfig = {
  // Prevent Next.js from redirecting /api/ trailing slashes — the FastAPI
  // backend handles its own slash normalization and the two redirects
  // create a loop in the browser.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
    ],
  },
};

module.exports = nextConfig;
