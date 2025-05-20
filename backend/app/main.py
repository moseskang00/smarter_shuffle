import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.endpoints import songs, auth, spotify


# ENV variables instantiation
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set"
        "For local development, set DATABASE_URL to a local postgres database"
        "For production, set DATABASE_URL to the remote database"
    )


app = FastAPI(
    title="Smarter Shuffle API",
    description="API for Spotify smart playlist generation using machine learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(songs.router, prefix="/api/songs", tags=["Songs"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(spotify.router, prefix="/api/spotify", tags=["Spotify"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 