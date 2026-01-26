from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Folosim calea absolută pentru fișierul SQLite
db_path = Path(__file__).parent.parent / "watermarkDB.sqlite"
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print(f"SQLite DB path: {db_path}")