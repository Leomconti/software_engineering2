from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.file_handler import FileHandler, FileRename
from app.handlers.room_handler import RoomCreate, RoomHandler
from app.services.database import get_db

router = APIRouter(tags=["rooms"])
templates = Jinja2Templates(directory="app/templates/rooms")


@router.get("/rooms")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await RoomHandler.get_rooms(db)


@router.post("/rooms")
async def create_room(request: Request, room: RoomCreate, db: AsyncSession = Depends(get_db)):
    return await RoomHandler.create_room(room, db)


@router.get("/rooms/{room_id}/{user_name}")
async def get_room(
    request: Request, 
    room_id: str, 
    user_name: str, 
    response_type: str = "html", 
    db: AsyncSession = Depends(get_db)
):
    """
    We've added response type conditional so it can return a json response or html, based on the request,
    this is really useful because of the integration tests, but also there are apis that use it so they can be 
    a rest api and serve static repsonseons.
    """
    room = await RoomHandler.get_room(room_id, db)
    files = await FileHandler.get_room_files(room_id, db)
    file_count = len(files)
    
    if response_type == "json":
        return {
            "room_name": room.name,
            "room_password": room.password,
            "files": files,
            "file_count": file_count,
            "room_id": room_id,
            "user_name": user_name,
        }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_name": room.name,
            "room_password": room.password,
            "files": files,
            "file_count": file_count,
            "room_id": room_id,
            "user_name": user_name,
        },
    )

@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await RoomHandler.delete_room(room_id, db)


@router.get("/rooms/{room_id}/files")
async def get_room_files(room_id: str, db: AsyncSession = Depends(get_db)):
    return await FileHandler.get_room_files(room_id, db)


@router.post("/rooms/{room_id}/{user_name}/files")
async def create_room_file(
    room_id: str, user_name: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    files = await FileHandler.get_room_files(room_id, db)
    file_count = len(files)
    if file_count >= 5:
        raise HTTPException(
            status_code=400, detail="Você atingiu o limite de arquivos na sala, exclua um arquivo para adicionar outro"
        )
    return await FileHandler.create_room_file(room_id, user_name, file, db)



@router.get("/files/{file_id}")
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)) -> FileResponse:
    file = await FileHandler.get_file(file_id, db)
    if file is None:
        raise HTTPException(
            status_code=404, detail="Houve um probleminha ao baixar o arquivo, tente novamente mais tarde"
        )
    return FileResponse(path=file.file_url)


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    return await FileHandler.delete_file(file_id, db)


@router.put("/files/{file_id}/rename")
async def rename_file(file_id: str, file_rename: FileRename, db: AsyncSession = Depends(get_db)):
    return await FileHandler.rename_file(file_id, file_rename.new_name, db)
