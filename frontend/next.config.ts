import type { NextConfig } from "next";

const production = process.env.NODE_ENV === "production";

// Next.js injects small inline bootstrap scripts, hence 'unsafe-inline' for scripts and
// styles; everything else is limited to this origin. Post media may live on any HTTPS
// host (CDN / Meta), so images and video allow https:. Dev mode needs eval for HMR,
// so the policy is only sent by production builds (`next start`).
const csp = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob: https:",
  "media-src 'self' blob: https:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join("; ");

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // Self-contained server (node server.js) with only the files it needs: small, non-root
  // production image (docker/frontend.prod.Dockerfile).
  output: "standalone",
  async headers() {
    const headers = [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "X-Frame-Options", value: "DENY" },
      { key: "Referrer-Policy", value: "no-referrer" },
      { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=()" },
      { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
    ];
    if (production) {
      headers.push({ key: "Content-Security-Policy", value: csp });
      // Ignored by browsers on plain HTTP (LAN testing); enforced once served over HTTPS.
      headers.push({ key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" });
    }
    return [{ source: "/:path*", headers }];
  },
};

export default nextConfig;
