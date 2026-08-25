from fastapi import APIRouter

from app.clients.resilient_client import ResilientAPIClient
from app.models.schemas import APIRequest, APIResponse
from app.services.retry_policy import RetryPolicy


router = APIRouter()


@router.post("/request", response_model=APIResponse)
async def make_request(request: APIRequest):

    policy = RetryPolicy(
        max_retries=request.retry_count
    )

    client = ResilientAPIClient(policy)

    result = await client.request(
        url=str(request.url),
        payload=request.payload,
        timeout=request.timeout,
        fallback_data=request.fallback_data,
    )

    return result