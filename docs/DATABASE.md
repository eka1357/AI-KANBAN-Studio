# Database Architecture

The application uses SQLite as its persistent data store. The database file is stored at `/app/data/kanban.db` inside the container, which is mounted to a Docker volume (`db_data`) so that data survives container restarts.

## Entities

As agreed for the MVP, we are using a simplified 2-table schema that directly stores the Kanban board as a JSON document. This satisfies the requirement to "save it as JSON" while keeping the backend implementation extremely simple.

### 1. `users`
Supports multiple users, satisfying the "database will support multiple users for future" requirement.
- **id**: INTEGER PRIMARY KEY
- **username**: TEXT UNIQUE (e.g., 'user')
- **password_hash**: TEXT (For MVP, this will just store the hash of 'password')

### 2. `boards`
Each user has exactly one board (MVP limitation).
- **user_id**: INTEGER PRIMARY KEY (Foreign key to users)
- **data**: JSON (The exact `BoardData` object expected by the frontend)

## Design Decisions

By storing the entire board as a single JSON blob:
1. `GET /api/board` simply retrieves the row for the authenticated user and returns the `data` column.
2. `PUT /api/board` simply overwrites the `data` column.
3. The AI structural output can directly replace or modify this JSON object without complex relational updates.
