# Backend: Kanban Studio

## Overview

Python FastAPI backend. Serves the app on port 8000. In Part 2 (scaffolding) it serves a hello-world HTML page and a health check. It will grow to serve the static Next.js build, provide API routes, manage SQLite, and proxy AI calls.

## Structure

- `main.py` — FastAPI application entry point; all routes live here until the app grows large enough to split
- `pyproject.toml` — Python project config; dependencies managed by `uv`
- `data/` — SQLite database volume mount point (created at container start); not committed to git

## Running locally (in Docker)

Use the scripts in `scripts/` — see `scripts/AGENTS.md`.

## Key routes (Part 2)

- `GET /` — hello-world HTML
- `GET /api/health` — returns `{"status": "ok"}`

## Dependency management

Uses `uv`. To add a dependency: add it to `pyproject.toml` under `[project] dependencies` and rebuild the Docker image.