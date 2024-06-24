import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.room_handler import RoomHandler, RoomCreate
from app.models import Room

"""
Commentarios para M3:
Aqui temos as funcoes de teste de integração relacionadas às rotas de salas.
Elas fazem o uso dos mocks criados em conftest (configuration for the test), para mockar o comportamento da db.
E utilizamos tambem o cliente fastapi criado no mock para testar as rotas.
"""

async def create_mock_room(db: AsyncSession, name="TesteRoom", password="pwd"):
    room = Room(name=name, password=password)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room

@pytest.mark.asyncio
async def test_create_room(client: TestClient):
    create_response: Response = client.post(
        "/rooms",
        json={"name": "TesteRoom", "password": "pwd", "create": True, "user_name": "UserDeTeste"},
    )
    assert create_response.status_code == 200, create_response.text
    response_json = create_response.json()
    assert "room_id" in response_json, f"Response JSON: {response_json}"
    assert "user_name" in response_json, f"Response JSON: {response_json}"
    assert response_json["user_name"] == "UserDeTeste"

@pytest.mark.asyncio
async def test_get_rooms(client: TestClient, db: AsyncSession):
    await create_mock_room(db)

    get_response: Response = client.get("/rooms")
    assert get_response.status_code == 200, get_response.text
    response_json = get_response.json()
    assert isinstance(response_json, list), f"Response JSON: {response_json}"
    assert len(response_json) > 0, "No rooms found in response"
    assert response_json[0]["name"] == "TesteRoom", f"Room name mismatch: {response_json[0]['name']}"

@pytest.mark.asyncio
async def test_get_room(client: TestClient, db: AsyncSession):
    room = await create_mock_room(db)

    get_response: Response = client.get(f"/rooms/{room.id}/UserDeTeste?response_type=json")
    assert get_response.status_code == 200, get_response.text
    response_json = get_response.json()
    assert "room_name" in response_json, f"Response JSON: {response_json}"
    assert response_json["room_name"] == room.name, f"Room name mismatch: {response_json['room_name']}"
    assert "room_password" in response_json, f"Response JSON: {response_json}"
    assert response_json["room_password"] == room.password, f"Room password mismatch: {response_json['room_password']}"