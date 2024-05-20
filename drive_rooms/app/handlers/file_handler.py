import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Files, Room


class FileRename(BaseModel):
    new_name: str


class FileHandler:
    @staticmethod
    async def get_room_files(room_id: str, db: AsyncSession):
        return await Files.get_all_by_room(db, room_id)

    @staticmethod
    async def get_file(file_id: str, db: AsyncSession):
        return await Files.get_by_id(db, file_id)

    @staticmethod
    async def delete_file(file_id: str, db: AsyncSession):
        await Files.delete_by_id(db, file_id)
        return {"message": "Arquivo excluído"}

    @staticmethod
    async def rename_file(file_id: str, new_name: str, db: AsyncSession):
        return await Files.update_by_id(db, file_id, name=new_name)

    @staticmethod
    async def create_room_file(room_id: str, user_name: str, file: UploadFile, db: AsyncSession):
        room = await Room.get(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Sala não encontrada")

        # Check if the room already has 5 files
        files = await Files.get_all_by_room(db, room_id)
        if len(files) >= 5:
            raise HTTPException(status_code=400, detail="Limite de 5 arquivos atingido")

        contents = await file.read()
        filename = file.filename if file.filename else uuid4().hex
        file_path = f"app/files/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(contents)

        new_file = Files(
            name=filename,
            extension=filename.split(".")[-1],
            room=room,
            file_url=f"uploads/{filename}",
            added_by=user_name,
        )
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)
        return {"filename": file.filename, "content_type": file.content_type}
