import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Files, Room


class FileHandler:
    @staticmethod
    async def get_room_files(room_id: str, db: AsyncSession):
        return await Files.get_all_by_room(db, room_id)

    @staticmethod
    async def create_room_file(room_id: str, user_name: str, file: UploadFile, db: AsyncSession):
        contents = await file.read()
        filename = file.filename if file.filename else uuid.uuid4().hex
        file_path = f"app/files/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(contents)

        room = await Room.get(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Sala não encontrada")

        new_file = Files(
            name=filename,
            extension=filename.split(".")[-1],
            room=room,
            file_url=f"uploads/{filename}",  # we send to uploads bc it's where we mount a static access from the api
            added_by=user_name,
        )
        db.add(new_file)
        await db.commit()
        return {"filename": file.filename, "content_type": file.content_type}

    @staticmethod
    async def get_file(file_id: str, db: AsyncSession):
        file = await Files.get_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        return file

    @staticmethod
    async def delete_file(file_id: str, db: AsyncSession):
        file = await Files.get_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        await Files.delete_by_id(db, file_id)
        return {"message": "Arquivo excluído"}
