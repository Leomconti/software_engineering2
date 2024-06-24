import pytest
from fastapi.testclient import TestClient
import os

"""
Commentarios for M3:
Aqui temos as funcoes de teste de integração.
Elas fazem o uso dos mocks criados em conftest (configuration for the test), para mockar o comportamento da db
E utilizamos tambem o cliente fastapi criado no mock para testar as rotas.
"""


@pytest.mark.asyncio
async def test_store_file_in_room(client: TestClient):
    create_response = client.post(
        "/rooms",
        json={"name": "Test Room", "password": "testpass", "create": True, "user_name": "testuser"},
    )
    room_id = create_response.json()["room_id"]

    file_path = "tests/artifacts/test_png.png"
    with open(file_path, "rb") as f:
        file_data = {
            "file": ("test_png.png", f, "image/png"),
        }
        store_response = client.post(f"/rooms/{room_id}/testuser/files", files=file_data)
        assert store_response.status_code == 200
        assert "id" in store_response.json()

@pytest.mark.asyncio
async def test_download_file_from_room(client: TestClient):
    create_response = client.post(
        "/rooms",
        json={"name": "Test Room", "password": "testpass", "create": True, "user_name": "testuser"},
    )
    room_id = create_response.json()["room_id"]

    file_path = "tests/artifacts/test_png.png"
    with open(file_path, "rb") as f:
        file_data = {
            "file": ("test_png.png", f, "image/png"),
        }
        store_response = client.post(f"/rooms/{room_id}/testuser/files", files=file_data)
        file_id = store_response.json()["id"]

    download_response = client.get(f"/files/{file_id}")
    assert download_response.status_code == 200
    with open(file_path, "rb") as f:
        assert download_response.content == f.read()