import uvicorn
from fastapi import FastAPI
from routes import listing

app = FastAPI()

app.include_router(listing.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
