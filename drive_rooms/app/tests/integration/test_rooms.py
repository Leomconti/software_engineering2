from httpx import Response
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.room_handler import RoomHandler, RoomCreate
from app.handlers.file_handler import FileHandler
from fastapi import HTTPException, UploadFile
from app.models import Room, Files

"""
Commentarios for M3:
Aqui temos as funcoes de teste de integração.
Elas fazem o uso dos mocks criados em conftest (configuration for the test), para mockar o comportamento da db
E utilizamos tambem o cliente fastapi criado no mock para testar as rotas.
"""

async def create_mock_room(db: AsyncSession, name="TesteRoom", password="pwd"):
    room = Room(name=name, password=password)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room

async def create_mock_file(db: AsyncSession, room, name="test.png", added_by="UserDeTeste"):
    extension = name.split(".")[-1]
    file = Files(name=name, room_id=str(room.id), file_url=f"uploads/{name}", added_by=added_by, extension=extension)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file

@pytest.mark.asyncio
async def test_store_file_in_room(client: TestClient):
    create_response: Response = client.post(
        "/rooms",
        json={"name": "TesteRoom", "password": "pwd", "create": True, "user_name": "UserDeTeste"},
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
        assert "id" in response_json, f"Response JSON: {response_json}"

@pytest.mark.asyncio
async def test_download_file_from_room(client: TestClient):
    create_response = client.post(
        "/rooms",
        json={"name": "TesteRoom", "password": "pwd", "create": True, "user_name": "testuser"},
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
        file_id = response_json.get("id")
        assert file_id is not None, f"File ID is None, Response JSON: {response_json}"

    download_response = client.get(f"/files/{file_id}")
    assert download_response.status_code == 200, download_response.text
    with open(file_path, "rb") as f:
        assert download_response.content == f.read()

@pytest.mark.asyncio
async def test_download_file_after_rename(db: AsyncSession):
    room = await create_mock_room(db)
    stored_file = await create_mock_file(db, room)
    await FileHandler.rename_file(stored_file.id, "new_test.png", db)
    await db.refresh(room)
    await db.refresh(stored_file)
    renamed_file = await FileHandler.get_file(stored_file.id, db)
    assert renamed_file is not None, "RenamedFile is None"
    assert renamed_file.name == "new_test.png", f"FileName: Expected 'new_test.png', got '{renamed_file.name}'"
    print(f"Renamed File: {renamed_file}")


@pytest.mark.asyncio
async def test_delete_room(db: AsyncSession):
    room = await create_mock_room(db)
    response = await RoomHandler.delete_room(room.id, db)
    assert response["message"] == "Sala excluída"
    deleted_room = await db.get(Room, room.id)
    assert deleted_room is None


@pytest.mark.asyncio
async def test_store_file_in_room_with_limit(client: TestClient):
    create_response: Response = client.post(
        "/rooms",
        json={"name": "TesteRoom", "password": "pwd", "create": True, "user_name": "UserDeTeste"},
    )
    assert create_response.status_code == 200, create_response.text
    room_id = create_response.json().get("room_id")
    assert room_id is not None, "Room ID is None"

    file_path = "tests/artifacts/test_png.png"
    file_data = {
        "file": ("test_png.png", open(file_path, "rb"), "image/png"),
    }

    for _ in range(5):
        store_response = client.post(f"/rooms/{room_id}/UserDeTeste/files", files=file_data)
        assert store_response.status_code == 200, store_response.text
    
    # After 5 files we expect to get 400 - exception flow
    store_response = client.post(f"/rooms/{room_id}/UserDeTeste/files", files=file_data)
    assert store_response.status_code == 400, store_response.text
    assert store_response.json().get("detail") == "Você atingiu o limite de arquivos na sala, exclua um arquivo para adicionar outro"