import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.room_handler import RoomHandler, RoomCreate

"""
Comentarios para M3:
Aqui temos os testes unitarios, vamos utilizar eles em cima das funcoes que sao os handlers da aplicacao, ou seja, 
que fazem as operacoes com room e com files.
"""

@pytest.mark.asyncio
async def test_create_room(db: AsyncSession):
    room = RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser")
    response = await RoomHandler.create_room(room, db)
    assert "room_id" in response, response
    assert "user_name" in response, response
    assert response["user_name"] == "testuser"

@pytest.mark.asyncio
async def test_delete_room(db: AsyncSession):
    room_response = await RoomHandler.create_room(RoomCreate(name="Test Room", password="testpass", create=True, user_name="testuser"), db)
    response = await RoomHandler.delete_room(room_response["room_id"], db)
    assert response["message"] == "Sala excluída"