import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import subscribers, reports

app = FastAPI(title="Analytics API")

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

# Routers
app.include_router(subscribers.router, prefix="/api/subscribers", tags=["Subscribers"])
app.include_router(reports.router, prefix="/api/reports", tags=["Digest"])


@app.get("/")
def root():
    return {"message": "Analytics API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
