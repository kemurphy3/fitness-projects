from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Use PostgreSQL by default, SQLite for local dev if specified
if settings.use_sqlite:
    DATABASE_URL = settings.sqlite_url
    connect_args = {"check_same_thread": False}
else:
    DATABASE_URL = settings.database_url
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
