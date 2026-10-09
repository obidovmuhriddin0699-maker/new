# syntax=docker/dockerfile:1
# Production image for the Next.js admin panel (standalone server).
#
#   docker build -f docker/frontend.prod.Dockerfile -t muxriddin-frontend:prod .
#
# The browser only ever talks to this server; it proxies the backend server-side
# (BACKEND_URL) and keeps the session JWT in an httpOnly cookie.

ARG NODE_IMAGE=node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402

# ------------------------------------------------------------------ dependencies
FROM ${NODE_IMAGE} AS deps
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

# ------------------------------------------------------------------ build
FROM deps AS build
COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------ production
FROM ${NODE_IMAGE} AS production
LABEL org.opencontainers.image.title="muxriddin-frontend" \
      org.opencontainers.image.description="MUXRIDDIN AI INSTAGRAM MANAGER admin panel"
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
WORKDIR /app
# The runtime is `node server.js`: drop the package managers bundled with the base image
# (no npm/npx/corepack/yarn to abuse, and their bundled dependencies' CVEs go with them).
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
           /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack \
           /usr/local/bin/yarn /usr/local/bin/yarnpkg /opt/yarn-* \
    && addgroup -S -g 10001 app && adduser -S -D -H -u 10001 -G app app
# Root-owned application files; only .next/cache (tmpfs in compose) must be writable.
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
USER app
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD ["node", "-e", "fetch('http://127.0.0.1:3000/login').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
CMD ["node", "server.js"]
