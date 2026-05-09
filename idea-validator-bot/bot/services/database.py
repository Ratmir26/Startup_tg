import asyncio
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Argument(Base):
    __tablename__ = "arguments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    idea_id = Column(String(36), ForeignKey("ideas.id"), nullable=False)
    type = Column(Enum("pro", "con", name="arg_type"), nullable=False)
    text = Column(Text, nullable=False)
    weight = Column(Enum("weak", "medium", "strong", name="arg_weight"), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self, url: str):
        if url.startswith("sqlite"):
            db_path = url.split("///")[-1]
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        self.engine = create_async_engine(url, echo=False)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        return self.session_factory()

    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> User:
        async with self.session_factory() as session:
            result = await session.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                user = User(id=user_id, username=username, first_name=first_name)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    async def create_idea(self, user_id: int, title: str) -> Idea:
        async with self.session_factory() as session:
            idea = Idea(user_id=user_id, title=title)
            session.add(idea)
            await session.commit()
            await session.refresh(idea)
            return idea

    async def get_user_ideas(self, user_id: int) -> list[Idea]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Idea)
                .filter(Idea.user_id == user_id)
                .order_by(Idea.updated_at.desc())
            )
            return list(result.scalars().all())

    async def get_idea(self, idea_id: str) -> Optional[Idea]:
        async with self.session_factory() as session:
            result = await session.execute(select(Idea).filter(Idea.id == idea_id))
            return result.scalar_one_or_none()

    async def delete_idea(self, idea_id: str):
        async with self.session_factory() as session:
            await session.execute(delete(Argument).filter(Argument.idea_id == idea_id))
            await session.execute(delete(Idea).filter(Idea.id == idea_id))
            await session.commit()

    async def add_argument(self, idea_id: str, arg_type: str, text: str, weight: str = "medium") -> Argument:
        async with self.session_factory() as session:
            arg = Argument(idea_id=idea_id, type=arg_type, text=text, weight=weight)
            session.add(arg)
            await session.commit()
            await session.refresh(arg)
            return arg

    async def get_idea_arguments(self, idea_id: str) -> tuple[list[Argument], list[Argument]]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Argument).filter(Argument.idea_id == idea_id).order_by(Argument.created_at)
            )
            args = list(result.scalars().all())
            pros = [a for a in args if a.type == "pro"]
            cons = [a for a in args if a.type == "con"]
            return pros, cons

    async def delete_argument(self, arg_id: str):
        async with self.session_factory() as session:
            await session.execute(delete(Argument).filter(Argument.id == arg_id))
            await session.commit()

    async def get_idea_full(self, idea_id: str) -> Optional[tuple[Idea, list[Argument], list[Argument]]]:
        idea = await self.get_idea(idea_id)
        if not idea:
            return None
        pros, cons = await self.get_idea_arguments(idea_id)
        return idea, pros, cons
