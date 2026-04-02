from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

load_dotenv()

SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")

engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
