import pytest
from httpx import AsyncClient
from app import app

# Test user login functionality
@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        payload = {
            "username": "JKTEST",
            "password": "JKTEST#123$"
        }
        response = await ac.post("/login/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

# Test login failure with incorrect credentials
@pytest.mark.asyncio
async def test_invalid_login():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        payload = {
            "username": "JKTEST",
            "password": "WrongPassword"
        }
        response = await ac.post("/login/", json=payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
