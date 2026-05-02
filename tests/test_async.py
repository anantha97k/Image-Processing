import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app


@pytest_asyncio.fixture(scope="function")
async def test_client():
    client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    )
    yield client


@pytest.mark.asyncio
async def test_main(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"test": 5}
