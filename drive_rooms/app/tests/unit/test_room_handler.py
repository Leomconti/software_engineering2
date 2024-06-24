import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.room_handler import RoomHandler, RoomCreate
import uuid
from fastapi import HTTPException

"""
Comentarios para M3:
Aqui temos os testes unitarios para RoomHandler.
"""

@pytest.mark.asyncio
async def test_create_room(db: AsyncSession):
    room = RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser")
    response = await RoomHandler.create_room(room, db)
    assert "room_id" in response, response
    assert "user_name" in response, response
    assert response["user_name"] == "testuser"

@pytest.mark.asyncio
async def test_create_room_already_exists(db: AsyncSession):
    room = RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser")
    await RoomHandler.create_room(room, db)
    
    with pytest.raises(HTTPException) as excinfo:
        await RoomHandler.create_room(room, db)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Sala com esse nome já existe"

@pytest.mark.asyncio
async def test_create_room_without_create_flag(db: AsyncSession):
    room_create = RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser")
    await RoomHandler.create_room(room_create, db)
    
    room = RoomCreate(name="Test Room", password="testpass", create=False, user_name="testuser")
    response = await RoomHandler.create_room(room, db)
    assert "room_id" in response, response
    assert "user_name" in response, response
    assert response["user_name"] == "testuser"

@pytest.mark.asyncio
async def test_create_room_with_incorrect_password(db: AsyncSession):
    room_create = RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser")
    await RoomHandler.create_room(room_create, db)
    
    room = RoomCreate(name="Test Room", password="wrongpass", create=False, user_name="testuser")
    with pytest.raises(HTTPException) as excinfo:
        await RoomHandler.create_room(room, db)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Senha incorreta"

@pytest.mark.asyncio
async def test_delete_room(db: AsyncSession):
    room_response = await RoomHandler.create_room(RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser"), db)
    response = await RoomHandler.delete_room(room_response["room_id"], db)
    assert response["message"] == "Sala excluída"

@pytest.mark.asyncio
async def test_delete_non_existent_room(db: AsyncSession):
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        await RoomHandler.delete_room(str(fake_id), db)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Sala nao encontrada"
