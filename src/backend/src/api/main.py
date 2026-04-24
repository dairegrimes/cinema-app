from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routes import listing
from db.repo.run import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Cinema Listings API", lifespan=lifespan)

app.include_router(listing.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
