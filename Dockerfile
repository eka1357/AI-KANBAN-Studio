# Stage 1: Build the Next.js frontend
FROM node:20-slim AS builder

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --no-dev --frozen

# Copy backend source
COPY backend/ .

# Copy built frontend
COPY --from=builder /app/out /app/static

# Ensure volume mount point exists
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
