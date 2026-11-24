import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from src import service
from src.crypto import check_key
from src.db import init_db
from src.routes import router

PURGE_INTERVAL_SECONDS = 60

async def _purge_loop():
    while True:
        try:
            await asyncio.to_thread(service.purge_expired)
        except Exception:
            pass
        await asyncio.sleep(PURGE_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    check_key()
    init_db()
    task = asyncio.create_task(_purge_loop())
    yield
    task.cancel()

app = FastAPI(title="VaultDrop", lifespan=lifespan)
app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Invalid input"})

@app.get("/health")
def health():
    return {"status": "ok"}


FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'
app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')
