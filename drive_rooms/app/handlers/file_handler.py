import os
import uuid

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Files, Room
from app.processors.file_processor_factory import FileProcessorFactory


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
        contents = await file.read()
        filename = file.filename if file.filename else uuid.uuid4().hex
        file_extension = filename.split(".")[-1].lower()
        file_path = f"app/uploads/{filename}"
        thumbnail_path = f"app/uploads/thumbnails/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(contents)

        room = await Room.get(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Sala não encontrada")

        # Generate thumbnail
        processor = FileProcessorFactory.get_processor(file_extension)
        await processor.generate_thumbnail(file_path, thumbnail_path)

        new_file = Files(
            name=filename,
            extension=file_extension,
            room=room,
            file_url=f"uploads/{filename}",
            added_by=user_name,
            thumbnail_url=f"uploads/thumbnails/{filename.replace('pdf', 'png')}",  # if it's pdf, the thumb goes to png, ugly to do here but works :)
        )
        db.add(new_file)
        await db.commit()
        return new_file
