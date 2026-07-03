from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from database import init_db, get_user_id, get_board, save_board
from models import BoardData
from auth import create_session, destroy_session, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login(req: LoginRequest, response: Response):
    user_id = await get_user_id(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user_id)
    # Set httponly cookie for session
    response.set_cookie(key="session", value=token, httponly=True, samesite="lax")
    return {"message": "Logged in"}

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("session")
    if token:
        destroy_session(token)
    response.delete_cookie("session")
    return {"message": "Logged out"}

@app.get("/api/board", response_model=BoardData)
async def read_board(user_id: int = Depends(get_current_user)):
    board = await get_board(user_id)
    if not board:
        # Return empty/default board if none exists
        # In this MVP, we let the frontend's initialData take over if we return 404 or empty.
        # But we can just return a basic empty board here.
        return BoardData(columns=[], cards={})
    return board

@app.put("/api/board")
async def update_board(board: BoardData, user_id: int = Depends(get_current_user)):
    await save_board(user_id, board)
    return {"status": "saved"}

class ChatRequest(BaseModel):
    message: str
    board: BoardData

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, user_id: int = Depends(get_current_user)):
    from ai import chat_with_ai
    
    response = await chat_with_ai(req.message, req.board)
    
    # If the AI modified the board, we should save it automatically
    if response.board:
        await save_board(user_id, response.board)
        
    return {
        "reply": response.message,
        "board": response.board.model_dump() if response.board else None
    }

# Serve the static files from Next.js export
if os.path.isdir("static"):
    app.mount("/_next", StaticFiles(directory="static/_next"), name="next")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side routing
        return FileResponse(os.path.join("static", "index.html"))
