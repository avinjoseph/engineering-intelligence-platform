import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:6543/sre_agent?sslmode=disable")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return SessionLocal()

def init_database():
    
    from models import (  # Import models here to ensure they are registered with Base       
        Base,
        Chunk,
        Document,
    )
    
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("Vector extension enabled.")
        
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

# This allows you to run this file directly from the terminal
if __name__ == "__main__":
    init_database()