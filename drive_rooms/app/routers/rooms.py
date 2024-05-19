import uuid

import models
from database import get_db
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["rooms"])
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

print("Templates", templates)


@router.get("/rooms")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await models.Room.get_all(db)


class RoomCreate(BaseModel):
    name: str
    password: str
    create: bool


@router.post("/rooms")
async def create_room(request: Request, room: RoomCreate, db: AsyncSession = Depends(get_db)):
    if room.create:
        existing_room = await models.Room.get_by_name(db, room.name)
        if existing_room:
            raise HTTPException(status_code=400, detail="Room with this name already exists")
        new_room = await models.Room.create(db, room.name, room.password)
        room_id = new_room.id
    else:
        existing_room = await models.Room.get_by_name(db, room.name)
        if not existing_room:
            raise HTTPException(status_code=404, detail="Room not found")
        if room.password != existing_room.password:
            raise HTTPException(status_code=400, detail="Password incorrect")

        room_id = existing_room.id

    return {"room_id": room_id}


@router.get("/rooms/{room_id}", response_class=HTMLResponse)
async def get_room(request: Request, room_id: str, db: AsyncSession = Depends(get_db)):
    room = await models.Room.get(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    files = await models.Files.get_all_by_room(db, room_id)
    return templates.TemplateResponse(
        "room.html",
        {"request": request, "room_name": room.name, "room_password": room.password, "files": files},
    )


@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str, db: AsyncSession = Depends(get_db)):
    await models.Room.delete_by_id(db, room_id)  # Use the correct method
    return {"message": "Room deleted"}


@router.get("/rooms/{room_id}/files")
async def get_room_files(room_id: str, db: AsyncSession = Depends(get_db)):
    return await models.Files.get_all_by_room(db, room_id)  # Use the correct method


class FileCreate(BaseModel):
    name: str
    extension: str


@router.post("/rooms/{room_id}/files")
async def create_room_file(room_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    contents = await file.read()
    if file.filename is None:
        filename = uuid.uuid4().hex
    else:
        filename = file.filename
    file_path = f"files/{filename}"
    with open(file_path, "wb") as f:
        f.write(contents)
    new_file = models.Files(name=filename, extension=filename.split(".")[-1], room=room_id, file_url=file_path)
    db.add(new_file)
    await db.commit()
    return {"filename": file.filename, "content_type": file.content_type}


@router.get("/files/{file_id}")
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)):
    file = await models.Files.get_by_id(db, file_id)  # Use the correct method
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file.file_url)


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    file = await models.Files.get_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    await models.Files.delete_by_id(db, file_id)
    return {"message": "File deleted"}
