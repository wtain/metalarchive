import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Double
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
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


    class Post(Base):
        __tablename__ = "posts"
        id = Column(Integer, primary_key=True)
        text = Column(String)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # todo: move into Post itself, handle updates
    class PostHeader(Base):
        __tablename__ = "posts_header"
        id = Column(Integer, primary_key=True)
        post_id = Column(Integer, ForeignKey("posts.id"), index=True)
        title = Column(String)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        post = relationship("Post")

    class PostTags(Base):
        __tablename__ = "posts_tags"
        id = Column(Integer, primary_key=True)
        post_id = Column(Integer, ForeignKey("posts.id"), index=True)
        name = Column(String)
        probability = Column(Double)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        post = relationship("Post")


    class PostMetric(Base):
        __tablename__ = "posts_metrics"
        id = Column(Integer, primary_key=True, autoincrement=True)
        post_id = Column(Integer, ForeignKey("posts.id"), index=True)
        # todo: remove
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        views = Column(Integer, default=0)
        reactions = Column(Integer, default=0)
        comments = Column(Integer, default=0)

        run_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=False)

        batch_run = relationship("BatchRun", back_populates="posts")
        post = relationship("Post")


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
