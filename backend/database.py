import aiosqlite
import json
import os
from models import BoardData

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join("/app/data", "kanban.db") if os.path.exists("/app/data") else "kanban.db",
)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS boards (
                user_id INTEGER PRIMARY KEY,
                data JSON NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        await db.commit()
        
        # Ensure 'user' exists with password 'password' for MVP
        # In a real app we'd hash this, but we'll store plaintext for this MVP
        # as it's hardcoded and only for demo purposes.
        await db.execute('''
            INSERT OR IGNORE INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ("user", "password"))
        await db.commit()

async def get_user_id(username: str, password: str) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', (username, password)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT username FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return {"id": user_id, "username": row[0]} if row else None

async def get_board(user_id: int) -> BoardData | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT data FROM boards WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return BoardData.model_validate_json(row[0])
            return None

async def save_board(user_id: int, board: BoardData):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO boards (user_id, data) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET data = excluded.data
        ''', (user_id, board.model_dump_json()))
        await db.commit()
