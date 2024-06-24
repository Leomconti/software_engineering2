import os
import uuid
import pytest
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.file_handler import FileHandler, FileRename
from app.models import Room, Files

"""
Comentarios para M3:
Aqui temos os testes unitarios para FileHandler.

Teremos testes em todas as operacoes de file, nos fluxos padrao e tambem alternativos.
"""

# Mocks em comum
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

def get_test_upload_file(file_path: str, filename: str) -> UploadFile:
    return UploadFile(filename=filename, file=open(file_path, "rb"))

# Fim dos mocks em comum, e arquivos de teste

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
