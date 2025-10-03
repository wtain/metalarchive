from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "postgresql://admin:admin@localhost:5432/telegram_metrics"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class BatchRun(Base):
    __tablename__ = "batch_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    posts = relationship("PostMetric", back_populates="batch_run")
    subscribers = relationship("Subscriber", back_populates="batch_run")


class PostMetric(Base):
    __tablename__ = "posts_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(BigInteger, index=True)
    # todo: remove
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    views = Column(Integer, default=0)
    reactions = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    run_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=False)

    batch_run = relationship("BatchRun", back_populates="posts")


class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    # todo: remove
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    run_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=False)

    batch_run = relationship("BatchRun", back_populates="subscribers")


# Create tables
Base.metadata.create_all(engine)
