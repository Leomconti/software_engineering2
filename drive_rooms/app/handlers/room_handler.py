from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Room


class RoomCreate(BaseModel):
    name: str
    password: str
    create: bool
    user_name: str

class RoomHandler:
    @staticmethod
    async def get_rooms(db: AsyncSession):
        return await Room.get_all(db)

    @staticmethod
    async def create_room(room: RoomCreate, db: AsyncSession):
        if room.create:
            existing_room = await Room.get_by_name(db, room.name)
            if existing_room:
                raise HTTPException(status_code=400, detail="Sala com esse nome já existe")
            new_room = await Room.create(db, room.name, room.password)
            return {"room_id": new_room.id, "user_name": room.user_name}
        else:
            existing_room = await Room.get_by_name(db, room.name)
            if not existing_room:
                raise HTTPException(status_code=404, detail="Sala não encontrada")
            if room.password != existing_room.password:
                raise HTTPException(status_code=400, detail="Senha incorreta")
            return {"room_id": existing_room.id, "user_name": room.user_name}

    @staticmethod
    async def get_room(room_id: str, db: AsyncSession):
        room = await Room.get(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Sala não encontrada")
        return room

    @staticmethod
    async def delete_room(room_id: str, db: AsyncSession):
        room = await Room.get(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Sala nao encontrada")
        await Room.delete_by_id(db, room_id)
        return {"message": "Sala excluída"}