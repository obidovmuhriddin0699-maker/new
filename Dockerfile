FROM node:22-alpine AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig*.json ./
COPY src ./src
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM python:3.13-slim AS backend
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    COOKIE_SECURE=true \
    FRONTEND_DIST_DIR=/app/frontend_dist
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY alembic.ini ./
COPY --from=frontend /app/dist ./frontend_dist
CMD ["python", "-m", "backend.production"]
