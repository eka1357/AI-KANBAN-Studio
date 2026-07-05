import os
# pyrefly: ignore [missing-import]
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# For MVP we will use openrouter
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-120b:free")
from models import BoardData
import json

class ChatResponse(BaseModel):
    message: str
    board: BoardData | None

async def chat_with_ai(user_message: str, current_board: BoardData) -> ChatResponse:
    system_prompt = """You are an AI assistant integrated into a Kanban board.
    The user will give you instructions to modify the board or ask questions.
    You must always reply with a JSON object containing two keys:
    1. "message": Your text response to the user.
    2. "board": The fully updated BoardData object. If no changes were requested, return null for "board".
    
    The BoardData object MUST conform to this schema:
    {
      "columns": [{ "id": "string", "title": "string", "cardIds": ["string"] }],
      "cards": { "card_id_string": { "id": "string", "title": "string", "details": "string" } }
    }
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Current Board JSON:\n{current_board.model_dump_json()}\n\nUser Message: {user_message}"}
    ]
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
        board_data = BoardData(**data["board"]) if data.get("board") else None
        return ChatResponse(message=data.get("message", "Done."), board=board_data)
    except Exception as e:
        print(f"AI Output parsing error: {e}")
        return ChatResponse(message="I had trouble updating the board correctly.", board=None)
