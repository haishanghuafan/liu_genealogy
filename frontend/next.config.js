/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React Strict Mode for better development experience
  reactStrictMode: true,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8012/api/v1',
  },

  // Proxy API requests to backend
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8012/api/v1/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
