import pytest
from httpx import AsyncClient
from app import app
from app import SessionLocal_test
from app import get_db
from app.models import Book

# Override the get_db dependency to use the test database session
@pytest.fixture(scope="function")
async def db_session():
    async with SessionLocal_test() as session:
        yield session

app.dependency_overrides[get_db] = db_session

# Test cases for book-related operations
@pytest.mark.asyncio
async def test_create_book(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Sci-Fi",
            "year_published": 2022,
            "summary": "Test summary"
        }
        response = await client.post("/books/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["author"] == "Test Author"

@pytest.mark.asyncio
async def test_get_books(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_update_book(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "title": "Updated Test Book",
            "author": "Updated Author",
            "genre": "Thriller",
            "year_published": 2021,
            "summary": "Updated summary"
        }
        response = await client.put("/books/1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Book"

@pytest.mark.asyncio
async def test_delete_book(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.delete("/books/1")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Book and its reviews deleted successfully!"
