import re

def ensure_asyncpg(url: str) -> str:
    u = url.strip().replace('postgres://', 'postgresql://')
    if u.startswith('postgresql+asyncpg://'):
        return u
    u = re.sub(r'^postgresql(?:\+psycopg2|\+psycopg)?://', 'postgresql+asyncpg://', u)
    if u.startswith('postgresql://'):
        u = 'postgresql+asyncpg://' + u[len('postgresql://'):]
    return u

from distutils.util import strtobool  # type: ignore

def _to_bool(v):
    if isinstance(v, bool):
        return v
    try:
        return bool(strtobool(str(v)))
    except Exception:
        return False

"""
Database configuration and connection
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import settings

# Create base class for models
Base = declarative_base()

# Async engine for async operations
async_engine = create_async_engine(
    ensure_asyncpg(settings.database_url),
    echo=_to_bool(settings.debug),
    pool_pre_ping=True,
    pool_recycle=300
)

# Sync engine for migrations and sync operations
sync_engine = create_engine(
    settings.database_url_sync,
    echo=_to_bool(settings.debug),
    pool_pre_ping=True,
    pool_recycle=300
)

# Session makers
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=sync_engine
)


async def get_async_session():
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def create_tables():
    """Create all tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

