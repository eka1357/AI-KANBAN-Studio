# Project Plan: Kanban Studio MVP

---

## Part 1: Plan (this document)

### Steps
- [x] Read and understand all existing frontend code
- [x] Create `frontend/AGENTS.md` describing the existing frontend
- [x] Enrich this PLAN.md with sub-steps, checklists, and success criteria for each part
- [x] Get user approval on the plan

### Success criteria
- This document is complete and approved by the user
- `frontend/AGENTS.md` exists and accurately describes the current code

---

## Part 2: Scaffolding

Set up the Docker infrastructure, the FastAPI backend, and start/stop scripts. Serve a hello-world HTML page and make an example API call to confirm everything works end-to-end.

### Steps
- [ ] Create `backend/main.py` with FastAPI app; add a `GET /api/health` route returning `{"status": "ok"}`
- [ ] Add a `GET /` route that serves a static hello-world HTML response
- [ ] Create `backend/pyproject.toml` declaring dependencies: `fastapi`, `uvicorn[standard]`
- [ ] Create `Dockerfile` at project root:
  - Uses `python:3.12-slim` base
  - Installs `uv`, uses it to sync deps from `pyproject.toml`
  - Copies backend source
  - Exposes port 8000, runs `uvicorn main:app`
- [ ] Create `docker-compose.yml` at project root:
  - Single service `app`, builds from `.`
  - Port mapping `8000:8000`
  - Mounts a named volume `db_data` at `/app/data` (for future SQLite)
  - Loads `.env` file for environment variables
- [ ] Create `scripts/start.sh` (Mac/Linux) and `scripts/start.ps1` (Windows):
  - Runs `docker compose up --build -d`
  - Prints the local URL on success
- [ ] Create `scripts/stop.sh` and `scripts/stop.ps1`:
  - Runs `docker compose down`
- [ ] Update `backend/AGENTS.md` to describe the backend structure
- [ ] Update `scripts/AGENTS.md` to describe the scripts

### Tests
- Run `scripts/start` script; container starts without error
- `curl http://localhost:8000/` returns the hello-world HTML
- `curl http://localhost:8000/api/health` returns `{"status":"ok"}`
- Run `scripts/stop` script; container stops cleanly

### Success criteria
- Docker build completes with no errors
- Both endpoints respond correctly on `localhost:8000`
- Start and stop scripts work on all three platforms

---

## Part 3: Add in Frontend

Build the Next.js frontend inside Docker and have FastAPI serve the static output at `/`.

### Steps
- [ ] Update `Dockerfile` to multi-stage build:
  - Stage 1 (`builder`): Node 20 slim, copy `frontend/`, run `npm ci` then `npm run build` (static export)
  - Stage 2 (`runtime`): Python 3.12 slim, install uv, sync backend deps, copy backend, copy static output from stage 1 into `/app/static`
- [ ] Update `frontend/next.config.ts` to set `output: "export"` and `distDir: "out"` for static export
- [ ] Update FastAPI to mount the `static/` directory and serve `index.html` as a fallback for all non-API routes
- [ ] Confirm the Kanban board renders correctly when the Docker container is running

### Tests
- Unit tests: `npm run test:unit` passes inside the container build step (or locally)
- Navigate to `http://localhost:8000/`; the Kanban board loads with columns and cards
- Drag a card between columns; it moves correctly
- Add a new card; it appears in the correct column
- Rename a column; the header updates

### Success criteria
- `docker compose up --build` produces a working Kanban board at `http://localhost:8000/`
- No JavaScript console errors in browser
- All existing unit tests pass

---

## Part 4: Fake user sign-in

Gate the Kanban board behind a login page. Credentials are hardcoded to `user` / `password`. Users can log out.

### Steps
- [ ] Create `frontend/src/app/login/page.tsx`: login form with username and password fields
- [ ] Add auth state management via a React context (`AuthContext`) or simple sessionStorage check
- [ ] On successful login (`user` / `password`), store a flag in `sessionStorage` and redirect to `/`
- [ ] In `frontend/src/app/page.tsx`, check auth state; redirect to `/login` if not authenticated
- [ ] Add a logout button in the Kanban board header that clears auth state and redirects to `/login`
- [ ] Style login page using existing CSS variables and design system

### Tests
- Navigating to `/` when not logged in redirects to `/login`
- Submitting wrong credentials shows an error message; no redirect
- Submitting `user` / `password` redirects to `/` and shows the board
- Clicking logout returns to `/login`; navigating to `/` again redirects back to `/login`
- Playwright e2e test covers the full login to board to logout flow

### Success criteria
- The board is inaccessible without authentication
- Login/logout flow works correctly after a Docker rebuild
- No hardcoded credentials appear in any location other than the single auth check

---

## Part 5: Database modeling

Design and document the SQLite schema for persisting the Kanban board.

### Steps
- [ ] Define the schema covering: `users`, `boards`, `columns`, `cards` tables
- [ ] Save schema as `docs/schema.json` (table definitions with column names, types, constraints)
- [ ] Create `docs/DATABASE.md` explaining the schema, relationships, and design decisions
- [ ] Get user sign-off on the schema before proceeding to Part 6

### Success criteria
- Schema supports multiple users (future-proofing), one board per user for MVP
- `docs/schema.json` and `docs/DATABASE.md` exist and are approved by user

---

## Part 6: Backend API

Implement FastAPI routes to read and write the Kanban board for the authenticated user. Create the SQLite database if it does not exist.

### Steps
- [ ] Create `backend/database.py`: SQLite connection using `aiosqlite`, init function that creates tables if missing, stores DB at `/app/data/kanban.db`
- [ ] Create `backend/models.py`: Pydantic models for `Card`, `Column`, `BoardData` matching the frontend types
- [ ] Create `backend/auth.py`: simple token-based auth (session token stored in a cookie); `login` and `logout` endpoints; `get_current_user` dependency
- [ ] Implement API routes in `backend/main.py`:
  - `POST /api/auth/login` — validate credentials, set session cookie
  - `POST /api/auth/logout` — clear session cookie
  - `GET /api/board` — return full board data for authenticated user
  - `PUT /api/board` — replace entire board state for authenticated user
- [ ] On first login for `user`, seed the board with `initialData` matching the frontend's default
- [ ] Add `pytest` and `httpx` to dev dependencies
- [ ] Write backend unit tests in `backend/tests/`:
  - Test DB init creates tables
  - Test login/logout
  - Test `GET /api/board` returns seeded data
  - Test `PUT /api/board` persists changes across requests

### Tests
- Run `pytest` inside the container; all tests pass
- `curl -X POST /api/auth/login` with correct credentials returns a session cookie
- `curl /api/board` with session cookie returns board JSON
- `curl -X PUT /api/board` with modified board; subsequent `GET` returns the updated board
- Restart container; board data persists (Docker volume)

### Success criteria
- All backend tests pass
- Board data survives container restart via volume mount
- Invalid credentials return 401; unauthenticated board access returns 401

---

## Part 7: Frontend + Backend integration

Wire the frontend to call the real backend API, making the board persistent.

### Steps
- [ ] Create `frontend/src/lib/api.ts`: typed fetch wrapper for `GET /api/board` and `PUT /api/board`
- [ ] Update `KanbanBoard` to load initial data from `GET /api/board` on mount (replace `initialData`)
- [ ] On every board state change (drag, add, delete, rename), call `PUT /api/board` with the latest state
- [ ] Update login page to call `POST /api/auth/login`; handle 401 errors
- [ ] Update logout to call `POST /api/auth/logout`
- [ ] Handle loading and error states simply (disable interactions while saving)

### Tests
- Unit tests: mock API calls; board initialises from API response
- Playwright e2e: login then add a card then reload; card still present
- Playwright e2e: rename a column then reload; new name still shown
- Playwright e2e: drag a card to another column then reload; card is in correct column

### Success criteria
- All board mutations are persisted to SQLite
- The board survives a full page reload
- All unit and e2e tests pass after a Docker rebuild

---

## Part 8: AI connectivity

Connect the backend to OpenRouter and verify AI calls work.

### Steps
- [ ] Add `openai` (OpenAI Python client, supports OpenRouter base URL) to backend deps
- [ ] Create `backend/ai.py`: initialise OpenAI client pointed at `https://openrouter.ai/api/v1` using `OPENROUTER_API_KEY` from env; expose an `async def chat(messages)` helper
- [ ] Add `POST /api/ai/test` route: sends a "What is 2+2?" message and returns the response text
- [ ] Write a backend test for the AI test route (skippable in CI with env flag if no key available)
- [ ] Confirm `.env` is loaded by `docker-compose.yml` and the key reaches the container

### Tests
- `curl -X POST /api/ai/test` returns a response containing `4`
- Missing or invalid API key returns a clear 500 error with a meaningful message

### Success criteria
- The AI call round-trips successfully with model `openai/gpt-oss-120b:free`
- No API key is committed to source control

---

## Part 9: AI with board context and Structured Outputs

Extend the AI endpoint so it always receives the current board state and the user's conversation, and responds with structured output that optionally updates the board.

### Steps
- [ ] Define Pydantic response schema in `backend/ai.py` with `message: str` and `board_update: BoardData | None = None`
- [ ] Update `POST /api/ai/chat` route:
  - Accept `{ "history": [...messages], "user_message": "..." }`
  - Fetch current board for the authenticated user
  - Build system prompt including full board JSON and instruction to optionally return a board_update
  - Call the model with structured output parsing
  - If `board_update` is set, persist the updated board to the DB
  - Return the AI response
- [ ] Write backend tests:
  - Mock the AI call; assert board is included in system prompt
  - Mock a response with `board_update`; assert DB is updated

### Tests
- `POST /api/ai/chat` with "move card X to Done" returns a response and board is updated in DB
- Subsequent `GET /api/board` reflects the AI's changes

### Success criteria
- AI always has full board context
- Structured output is reliably parsed
- Board updates from AI are persisted atomically

---

## Part 10: AI sidebar UI

Add an AI chat sidebar to the frontend. Board updates from the AI trigger an automatic refresh.

### Steps
- [ ] Create `frontend/src/components/AISidebar.tsx`:
  - Collapsible panel on the right side
  - Chat history display (user and assistant messages)
  - Text input and send button
  - Single-response display (no streaming for simplicity)
- [ ] Integrate `AISidebar` into `KanbanBoard.tsx` layout
- [ ] On AI response, if `board_update` is present, update the board state in React (triggers re-render)
- [ ] Create `chatWithAI(history, message)` function in `frontend/src/lib/api.ts`
- [ ] Style the sidebar using existing CSS variables; match the Kanban board's visual language
- [ ] Add a toggle button in the header to open/close the sidebar

### Tests
- Unit test: `AISidebar` renders messages correctly
- Playwright e2e: open sidebar, send a message, assistant response appears
- Playwright e2e: ask AI to add a card, card appears on the board without a page reload

### Success criteria
- AI sidebar feels native to the app design
- Board updates from AI are reflected immediately in the UI
- All tests pass after a Docker rebuild
- Full user journey works: login, use board, chat with AI, AI modifies board, see live update