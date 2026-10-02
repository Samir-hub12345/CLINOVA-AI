# ==============================================================================
# CLINOVA AI - Frontend Container Image (Production Deployment Only)
#
# Note: For local Windows development, run natively with PowerShell:
#   .\scripts\clinova.ps1 start
#
# This Dockerfile is used by:
#   infrastructure/docker/docker-compose.prod.yml
# ==============================================================================

FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
