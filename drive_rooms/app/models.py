from uuid import uuid4

from database import Base
from sqlalchemy import Boolean, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    files = relationship(
        "Files", back_populates="room"
    )  # This is a 1 -> many relationship, it's just sugar from sqlalchemy to be abble to access more easily

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_all(cls, db: AsyncSession):
        result = await db.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
            if transaction is None:
                raise NoResultFound
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: str):
        transaction = await db.get(cls, id)
        if transaction is None:
            raise NoResultFound
        await db.delete(transaction)
        await db.commit()

    @classmethod
    async def create(cls, db: AsyncSession, name: str, password: str):
        new_room = cls(name=name, password=password)
        db.add(new_room)
        await db.commit()
        await db.refresh(new_room)
        return new_room


class Files(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    extension: Mapped[str] = mapped_column(String, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    room = relationship("Room", back_populates="files")

    @classmethod
    async def get_all_by_room(cls, db: AsyncSession, room_id: str):
        stmt = select(cls).where(cls.room_id == room_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
            if transaction is None:
                raise NoResultFound
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def delete_by_id(cls, db: AsyncSession, id: str):
        transaction = await db.get(cls, id)
        if transaction is None:
            raise NoResultFound
        await db.delete(transaction)
        await db.commit()

    @classmethod
    async def update_by_id(cls, db: AsyncSession, id: str, **kwargs):
        transaction = await db.get(cls, id)
        if transaction is None:
            raise NoResultFound
        for key, value in kwargs.items():
            setattr(transaction, key, value)
        await db.commit()
        return transaction
