import uvicorn
from fastapi import FastAPI
from api import subscribers, reactions

app = FastAPI(title="Analytics API")

# Routers
app.include_router(subscribers.router, prefix="/subscribers", tags=["Subscribers"])
app.include_router(reactions.router, prefix="/reactions", tags=["Reactions"])


@app.get("/")
def root():
    return {"message": "Analytics API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
