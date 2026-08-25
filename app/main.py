from fastapi import FastAPI

from app.api.routes import router as api_router
from app.simulator.flaky_api import router as flaky_router


app = FastAPI(
    title="Resilient API Client",
    description=(
        "A resilient HTTP client with retries, exponential backoff, "
        "timeout handling, and fallback support."
    ),
    version="1.0.0",
)


app.include_router(api_router)
app.include_router(flaky_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}