import logging
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import subscribers, reports, posts, updater
from api.updater import update_data

# logger = logging.getLogger(__name__)
logger = log = logging.getLogger("uvicorn.info")


# def heartbeat():
#     logger.info(datetime.now())


def scheduled_update():
    logger.info("Running scheduled update")
    update_data()


@asynccontextmanager
async def lifespan(app:FastAPI):
    scheduler = BackgroundScheduler()
    # scheduler.add_job(heartbeat, "interval", minutes=1)
    scheduler.add_job(scheduled_update, "interval", hours=1)
    scheduler.start()
    yield


app = FastAPI(title="Analytics API", lifespan=lifespan)
# app = FastAPI(title="Analytics API")

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
def root():
    return {"message": "Analytics API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
