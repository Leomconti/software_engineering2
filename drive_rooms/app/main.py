import os
from contextlib import asynccontextmanager

from database import get_db, sessionmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Files, Room
from routers.rooms import router as room_router
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

sessionmanager.init(os.getenv("DATABASE_URL"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(room_router) 

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/room/{room_id}", response_class=HTMLResponse)
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    room = await Room.get(db, room_id)
    if not room:
        return HTMLResponse(content="Room not found", status_code=404)
    
    files = await Files.get_all_by_room(db, room_id)
    
    return templates.TemplateResponse("room.html", {
        "request": Request,
        "room_name": room.name,
        "room_password": room.password,
        "files": files
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

