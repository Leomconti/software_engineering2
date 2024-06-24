import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.room_handler import RoomHandler, RoomCreate
import uuid
from fastapi import HTTPException
import os
import pytest
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.file_handler import FileHandler, FileRename
from app.models import Room, Files
from unittest.mock import MagicMock, patch
import uuid

"""
Comentarios para M3:
Aqui temos os testes unitarios, vamos utilizar eles em cima das funcoes que sao os handlers da aplicacao, ou seja, 
que fazem as operacoes com room e com files.
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


def get_test_upload_file(file_path: str, filename: str) -> UploadFile:
    return UploadFile(filename=filename, file=open(file_path, "rb"))

@pytest.mark.asyncio
async def test_create_room_file(db: AsyncSession):
    room = await create_mock_room(db)
    file_path = "tests/artifacts/test_png.png"
    upload_file = get_test_upload_file(file_path, "test_png.png")

    response = await FileHandler.create_room_file(str(room.id), "UserDeTeste", upload_file, db)
    assert "id" in response, response

    new_file = await db.get(Files, response["id"])
    assert new_file is not None
    assert new_file.name == "test_png.png"
    assert new_file.added_by == "UserDeTeste"

@pytest.mark.asyncio
async def test_get_file(db: AsyncSession):
    room = await create_mock_room(db)
    stored_file = await create_mock_file(db, room)
    file = await FileHandler.get_file(str(stored_file.id), db)
    assert file is not None
    assert file.id == stored_file.id

@pytest.mark.asyncio
async def test_get_non_existent_file(db: AsyncSession):
    non_existent_file_id = str(uuid.uuid4())
    file = await FileHandler.get_file(non_existent_file_id, db)
    assert file is None

@pytest.mark.asyncio
async def test_delete_file(db: AsyncSession):
    room = await create_mock_room(db)
    stored_file = await create_mock_file(db, room)
    response = await FileHandler.delete_file(str(stored_file.id), db)
    assert response["message"] == "Arquivo excluído"
    deleted_file = await db.get(Files, stored_file.id)
    assert deleted_file is None

@pytest.mark.asyncio
async def test_rename_file(db: AsyncSession):
    room = await create_mock_room(db)
    stored_file = await create_mock_file(db, room)
    await FileHandler.rename_file(str(stored_file.id), "new_test.png", db)
    await db.refresh(room)
    await db.refresh(stored_file)
    renamed_file = await FileHandler.get_file(str(stored_file.id), db)
    assert renamed_file is not None
    assert renamed_file.name == "new_test.png"