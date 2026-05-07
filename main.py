from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.ai import router as ai_router
from scalar_fastapi import get_scalar_api_reference


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs startup/shutdown logic. Like Node's process.on('ready')."""
    from app.dependencies.auth import PUBLIC_KEY
    if PUBLIC_KEY:
        print("✅  public.pem loaded — Zero-Trust auth active")
    else:
        print("⚠️  WARNING: public.pem missing — protected routes will fail")
    yield  # Server runs while paused here
    print("Korix AI Service shutting down.")


app = FastAPI(title="Korix AI Service", version="1.0.0", lifespan=lifespan)
app.include_router(ai_router)


@app.get("/")
async def health():
    return {"status": "ok"}

@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Korix AI Service",
    )



