import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.routers.rooms import router as room_router
from app.services.database import sessionmanager

load_dotenv()


async def check_db_connection():
    async with sessionmanager.session() as session:
        print("Checking database connection...")
        await session.execute(select(1))
        print("Database connection successful")


def init_app() -> FastAPI:
    sessionmanager.init(str(os.getenv("DATABASE_URL")))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await check_db_connection()
        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    server = FastAPI(debug=True, lifespan=lifespan)
    server.mount("/static", StaticFiles(directory="app/static"), name="static")
    server.mount("/files", StaticFiles(directory="app/files"), name="files")

    @server.get("/")
    async def read_root():
        return FileResponse("app/templates/index.html")

    server.include_router(room_router)

    return server
