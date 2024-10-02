import pytest
from httpx import AsyncClient
from app import app

# Test recommendations model
@pytest.mark.asyncio
async def test_recommendations(db_session):
    books = [
        {"title": "Book A", "author": "Author 1", "genre": "Sci-Fi", "year_published": 2022, "summary": "Summary A", "average_rating": 4.5},
        {"title": "Book B", "author": "Author 2", "genre": "Sci-Fi", "year_published": 2021, "summary": "Summary B", "average_rating": 4.0},
        {"title": "Book C", "author": "Author 3", "genre": "Fantasy", "year_published": 2020, "summary": "Summary C", "average_rating": 3.5},
    ]

    for book in books:
        response = await AsyncClient(app=app, base_url="http://testserver").post("/books/", json=book)
        assert response.status_code == 200

    response = await AsyncClient(app=app, base_url="http://testserver").get("/recommendations?book_title=Book A")
    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) > 0

# Test Llama3 model for summary generation
@pytest.mark.asyncio
async def test_generate_summary():
    payload = {"content": "This is a detailed content about a book that should be summarized."}
    async with AsyncClient(app=app, base_url="http://llama3_service:8001") as client:
        response = await client.post("/generate-summary/", json=payload)
        assert response.status_code == 200
        summary = response.json().get("summary")
        assert summary is not None
