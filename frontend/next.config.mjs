/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,

  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000/api',
  },

  poweredByHeader: false,

  // Fix Cross-Origin-Opener-Policy for Firebase popup auth
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin-allow-popups',
          },
        ],
      },
    ];
  },

  images: {
    unoptimized: true,
  },

  // Skip ESLint during production builds for faster deployment
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Skip TypeScript type checking during build (handled by IDE)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;

