from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Start with SQLite for dev; later swap the URL for Postgres
DATABASE_URL = "sqlite:///./soccer_app.db"
# For Postgres, it would look like:
# DATABASE_URL = "postgresql://username:password@localhost/dbname"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
