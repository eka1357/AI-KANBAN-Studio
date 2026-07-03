import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set env before importing app
os.environ["DB_PATH"] = "test_kanban.db"

from main import app
from database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Before test
    import database
    database.DB_PATH = "test_kanban.db"
    
    # Remove old test DB if it exists
    if os.path.exists("test_kanban.db"):
        os.remove("test_kanban.db")
        
    await init_db()
    
    yield
    
    # After test
    if os.path.exists("test_kanban.db"):
        os.remove("test_kanban.db")

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_auth_and_board(async_client: AsyncClient):
    # Test unauthorized access
    response = await async_client.get("/api/board")
    assert response.status_code == 401
    
    # Test login with hardcoded creds from init_db
    login_data = {"username": "user", "password": "password"}
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    # Ensure cookie is set
    assert "session" in response.cookies
    
    # Test GET board (should be empty initially, returns empty board)
    response = await async_client.get("/api/board")
    assert response.status_code == 200
    board_data = response.json()
    assert board_data["columns"] == []
    assert board_data["cards"] == {}
    
    # Test PUT board
    new_board = {
        "columns": [{"id": "col-1", "title": "Todo", "cardIds": ["c1"]}],
        "cards": {"c1": {"id": "c1", "title": "Test Card", "details": "Desc"}}
    }
    response = await async_client.put("/api/board", json=new_board)
    assert response.status_code == 200
    assert response.json() == {"status": "saved"}
    
    # Test GET board again
    response = await async_client.get("/api/board")
    assert response.status_code == 200
    assert response.json() == new_board
    
    # Test logout
    response = await async_client.post("/api/auth/logout")
    assert response.status_code == 200
    
    # Wait, the cookie is deleted, httpx AsyncClient handles cookies automatically,
    # let's verify if we can access the board after logout
    response = await async_client.get("/api/board")
    assert response.status_code == 401
