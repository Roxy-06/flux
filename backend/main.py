# Main FastAPI entry point for Amica application lifecycle, CORS, and routing.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.database import init_db
from api.repos import router as repos_router
from api.graph import router as graph_router
from api.understanding import router as understanding_router
from api.files import router as files_router
from api.issues import router as issues_router
from api.capsule import router as capsule_router


# Application lifespan handler initializing SQLite schemas on startup.
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Amica API", version="0.1.0", lifespan=lifespan)

# CORS middleware configuration for frontend communication
cors_origins = settings.cors_origins or ["*"]
allow_all = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router mounts
app.include_router(repos_router)
app.include_router(graph_router)
app.include_router(understanding_router)
app.include_router(files_router)
app.include_router(issues_router)
app.include_router(capsule_router)


# System health check endpoint.
@app.get("/api/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "app": "amica"}


# Starts the development server using configured host and port settings.
def main():
    import uvicorn
    uvicorn.run("main:app", host=settings.backend_host, port=settings.backend_port, reload=True)


if __name__ == "__main__":
    main()
