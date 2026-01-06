import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from api import subscribers, reports, posts, updater, tags
from api.updater import update_data
import logging.config
from logging_config import LOGGING_CONFIG
from metrics.middleware import MetricsMiddleware
from storage_client.models import SessionLocal


logging.config.dictConfig(LOGGING_CONFIG)

# logger = logging.getLogger(__name__)
logger = logging.getLogger("uvicorn.info")


# def heartbeat():
#     logger.info(datetime.now())


def scheduled_update():
    logger.info("Running scheduled update")
    update_data(SessionLocal())


@asynccontextmanager
async def lifespan(app:FastAPI):
    scheduler = BackgroundScheduler()
    # scheduler.add_job(heartbeat, "interval", minutes=1)
    scheduler.add_job(scheduled_update, "interval", minutes=15)
    scheduler.start()
    yield


app = FastAPI(title="Analytics API", lifespan=lifespan)
# app = FastAPI(title="Analytics API")

origins = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")


# origins = [
#     "http://localhost",
#     "http://localhost:5173",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)

# @app.on_event('startup')
# def init_data():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(scheduled_update, 'cron', hour='*')
#     scheduler.add_job(heartbeat, 'cron', minute='*')
#     scheduler.start()

# Routers
app.include_router(subscribers.router, prefix="/api/subscribers", tags=["Subscribers"])
app.include_router(reports.router, prefix="/api/reports", tags=["Digest"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(updater.router, prefix="/api/updater", tags=["Update"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])


@app.get("/")
def root():
    return {"message": "Analytics API is running"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run(app,
                host="127.0.0.1",
                port=8001,
                log_config=LOGGING_CONFIG)
