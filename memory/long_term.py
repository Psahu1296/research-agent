from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Text, DateTime
from datetime import datetime, timezone
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(String(500))
    report: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_session(topic: str, report: str):
    async with AsyncSessionLocal() as session:
        record = ResearchSession(topic=topic, report=report)
        session.add(record)
        await session.commit()

async def get_recent_sessions(limit: int = 3) -> list[dict]:
    from sqlalchemy import select, desc
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ResearchSession).order_by(desc(ResearchSession.created_at)).limit(limit)
        )
        rows = result.scalars().all()
        return [{"topic": r.topic, "report": r.report[:300]} for r in rows]
