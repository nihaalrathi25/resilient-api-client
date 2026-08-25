import asyncio

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse


router = APIRouter()

_request_count = 0


@router.post("/flaky")
async def flaky_api(
    failures: int = Query(default=2, ge=0, le=10),
    failure_type: int = Query(default=503),
    delay: float = Query(default=0, ge=0, le=30),
):
    global _request_count

    _request_count += 1

    if delay > 0:
        await asyncio.sleep(delay)

    if _request_count <= failures:
        print(
            f"[SIMULATOR] Request {_request_count}: "
            f"Returning HTTP {failure_type}"
        )

        return JSONResponse(
            status_code=failure_type,
            content={
                "status": "simulated_failure",
                "request_number": _request_count,
                "error": f"Simulated HTTP {failure_type}",
            },
        )

    print(
        f"[SIMULATOR] Request {_request_count}: "
        "Returning HTTP 200"
    )

    return {
        "status": "success",
        "message": "Simulated API succeeded",
        "request_number": _request_count,
    }