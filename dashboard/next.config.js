/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.discordapp.com',
      },
    ],
  },
  webpack: (config) => {
    config.cache = false
    return config
  }
}

module.exports = nextConfig