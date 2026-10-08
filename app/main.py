from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import APP_TITLE, APP_VERSION, BASE_DIR
from app.database import init_db
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    init_db()
    yield


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Scalable backend API & dashboard for bulk PDF certificate generation with status tracking and retrieval.",
    lifespan=lifespan
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files Directory
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API Router
app.include_router(api_router)


@app.get("/", tags=["Dashboard UI"])
def serve_dashboard():
    """Serves the interactive frontend web dashboard."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "title": APP_TITLE,
        "version": APP_VERSION,
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health & System"])
def health_check():
    return {"status": "healthy"}
