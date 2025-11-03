from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .init_db import init_db
from .routers.workers import router as workers_router


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(workers_router)

