import pytest
from httpx import AsyncClient
from app import app
from app.models import Book, Review

@pytest.mark.asyncio
async def test_add_review(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Create a book in the database
        book = Book(title="Test Book", author="Test Author", genre="Sci-Fi", year_published=2023, summary="Test summary")
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)

        review_payload = {
            "user_id": 1,
            "review_text": "This is a test review",
            "rating": 5
        }

        response = await client.post(f"/books/{book.id}/reviews", json=review_payload)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["review_text"] == "This is a test review"
        assert response_json["rating"] == 5

@pytest.mark.asyncio
async def test_get_reviews(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Create a book in the database
        book = Book(title="Test Book", author="Test Author", genre="Sci-Fi", year_published=2023, summary="Test summary")
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)

        review1 = Review(book_id=book.id, user_id=1, review_text="Great book!", rating=5)
        review2 = Review(book_id=book.id, user_id=2, review_text="Not bad", rating=3)
        db_session.add_all([review1, review2])
        await db_session.commit()

        response = await client.get(f"/books/{book.id}/reviews?skip=0&limit=10")
        assert response.status_code == 200
        reviews = response.json()
        assert len(reviews) == 2
        assert reviews[0]["review_text"] == "Great book!"
        assert reviews[1]["review_text"] == "Not bad"
