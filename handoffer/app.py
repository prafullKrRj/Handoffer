from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import discover, load_settings, save_settings
from .models import Settings, SettingsPatch, StatusResponse
from .providers import all_status

app = FastAPI(title="Handoffer", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8765", "http://localhost:8765"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "web"), name="static")


@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    settings = discover(load_settings())
    return StatusResponse(agents=await all_status(settings.providers), policy={"threshold_percent": settings.threshold_percent, "auto_delegate": settings.auto_delegate})


@app.post("/api/refresh", response_model=StatusResponse)
async def refresh() -> StatusResponse:
    return await get_status()


@app.get("/api/settings", response_model=Settings)
async def get_settings() -> Settings:
    return load_settings()


@app.put("/api/settings", response_model=Settings)
async def put_settings(patch: SettingsPatch) -> Settings:
    settings = load_settings()
    if patch.threshold_percent is not None:
        settings.threshold_percent = patch.threshold_percent
    if patch.auto_delegate is not None:
        settings.auto_delegate = patch.auto_delegate
    return save_settings(settings)


@app.get("/")
async def dashboard() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "web" / "index.html")
