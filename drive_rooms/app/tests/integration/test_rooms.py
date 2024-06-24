import pytest
from fastapi.testclient import TestClient

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
    assert create_response.status_code == 200, create_response.text
    room_id = create_response.json().get("room_id")
    assert room_id is not None, "Room ID is None"

    file_path = "tests/artifacts/test_png.png"
    with open(file_path, "rb") as f:
        file_data = {
            "file": ("test_png.png", f, "image/png"),
        }
        store_response = client.post(f"/rooms/{room_id}/testuser/files", files=file_data)
        assert store_response.status_code == 200, store_response.text
        response_json = store_response.json()
        print("Store Response JSON:", response_json)  # Debugging
        assert "id" in response_json, f"Response JSON: {response_json}"

@pytest.mark.asyncio
async def test_download_file_from_room(client: TestClient):
    create_response = client.post(
        "/rooms",
        json={"name": "Test Room", "password": "testpass", "create": True, "user_name": "testuser"},
    )
    assert create_response.status_code == 200, create_response.text
    room_id = create_response.json().get("room_id")
    assert room_id is not None, "Room ID is None"

    file_path = "tests/artifacts/test_png.png"
    with open(file_path, "rb") as f:
        file_data = {
            "file": ("test_png.png", f, "image/png"),
        }
        store_response = client.post(f"/rooms/{room_id}/testuser/files", files=file_data)
        assert store_response.status_code == 200, store_response.text
        response_json = store_response.json()
        print("Store Response JSON:", response_json)  # Debugging
        file_id = response_json.get("id")
        assert file_id is not None, f"File ID is None, Response JSON: {response_json}"

    download_response = client.get(f"/files/{file_id}")
    assert download_response.status_code == 200, download_response.text
    with open(file_path, "rb") as f:
        assert download_response.content == f.read()