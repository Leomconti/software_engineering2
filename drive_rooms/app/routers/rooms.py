import models
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["rooms"])

@router.get("/rooms")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return db.query(models.Room).all()


class RoomCreate(BaseModel):
    name: str
    password: str
    create: bool


@router.post("/rooms")
async def create_room(room: RoomCreate, db: AsyncSession = Depends(get_db)):
    if room.create:
        # Check if room with the same name already exists
        existing_room = await models.Room.get_by_name(db, room.name)
        if existing_room:
            raise HTTPException(status_code=400, detail="Room already exists")
        
        # Create new room using the new create method
        new_room = await models.Room.create(db, room.name, room.password)
        return new_room
    else:
        # Search for existing room
        existing_room = await models.Room.get_by_name(db, room.name)
        if not existing_room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Check password
        if room.password == existing_room.password:
            return existing_room
        else:
            raise HTTPException(status_code=400, detail="Password incorrect")
@router.get("/rooms/{room_id}")
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    return db.query(models.Room).filter(models.Room.id == room_id).first()


@router.delete("/rooms/{room_id}")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    db.delete(models.Room).filter(models.Room.id == room_id)
    await db.commit()
    return {"message": "Room deleted"}


@router.get("/rooms/{room_id}/files")
async def get_room_files(room_id: int, db: AsyncSession = Depends(get_db)):
    return db.query(models.File).filter(models.File.room_id == room_id).all()

class FileCreate(BaseModel):
    name: str
    extension: str


@router.post("rooms/{room_id}/files")
async def create_room_file(room_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    contents = await file.read()
    # save file to hard drive
    with open(f"files/{file.filename}", "wb") as f:
        f.write(contents)
    db.add(models.File(name=file.filename, extension=file.filename.split('.')[-1], room_id=room_id))
    await db.commit()
    return {"filename": file.filename, "content_type": file.content_type}


@router.get("files/{file_id}")
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)):
    file: models.Files = await models.File.get_by_id(db, file_id)
    file_path = file.file_url
    return FileResponse(file_path)
