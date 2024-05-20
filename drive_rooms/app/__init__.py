import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.routers.rooms import router as room_router
from app.services.database import sessionmanager

load_dotenv()


async def check_db_connection():
    async with sessionmanager.session() as session:
        print("Starting database connection...")
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
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    server.mount("/static", StaticFiles(directory="app/static"), name="static")  # Static stuff, like css
    server.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")  # Uploaded files
    templates = Jinja2Templates(directory="app/templates/home")  # Template for home page

    # Entry point, home page here!
    @server.get("/")
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    server.include_router(room_router)

    return server
