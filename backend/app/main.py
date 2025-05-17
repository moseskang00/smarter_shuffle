import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.endpoints import songs

load_dotenv()

app = FastAPI(
    title="Smarter Shuffle API",
    description="API for Spotify smart playlist generation using machine learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include our songs router
app.include_router(songs.router, prefix="/api/songs", tags=["Songs"])

# Import and include routers
# @app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# @app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])
# @app.include_router(playlist.router, prefix="/playlist", tags=["Playlist"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 