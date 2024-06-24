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
        file_dir = os.path.join("app", "uploads")
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)
        thumbnail_dir = os.path.join(file_dir, "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_path = os.path.join(thumbnail_dir, filename)

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
            file_url=file_path,
            added_by=user_name,
            thumbnail_url=thumbnail_path,
        )
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)
        return {"id": new_file.id}