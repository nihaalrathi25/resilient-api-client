import asyncio

import httpx

from app.services.retry_policy import RetryPolicy
from app.utils.logger import get_logger


class ResilientAPIClient:
    def __init__(self, retry_policy: RetryPolicy):
        self.retry_policy = retry_policy
        self.logger = get_logger(__name__)

    async def request(
        self,
        url: str,
        payload: dict,
        timeout: float,
        fallback_data: dict | None = None,
    ):
        attempts = 0
        max_attempts = self.retry_policy.max_retries + 1

        while attempts < max_attempts:
            attempts += 1

            try:
                self.logger.info(
                    f"Attempt {attempts}/{max_attempts} -> {url}"
                )

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        url,
                        json=payload,
                    )

                self.logger.info(
                    f"Received HTTP {response.status_code}"
                )

                # Successful response
                if response.status_code < 400:
                    try:
                        data = response.json()
                    except ValueError:
                        data = response.text

                    self.logger.info(
                        f"Request successful on attempt {attempts}"
                    )

                    return {
                        "status": "success",
                        "response": data,
                        "attempts": attempts,
                        "retry_attempts": attempts - 1,
                        "fallback_used": False,
                        "error": None,
                    }

                # Non-transient errors should not be retried
                if not self.retry_policy.should_retry(
                    response.status_code,
                    attempts,
                ):
                    self.logger.error(
                        f"Non-retryable HTTP error: "
                        f"{response.status_code}"
                    )
                    break

                # Retry transient errors
                if attempts < max_attempts:
                    delay = self.retry_policy.get_backoff(attempts)

                    self.logger.warning(
                        f"Transient HTTP {response.status_code}. "
                        f"Retrying in {delay:.2f}s"
                    )

                    await asyncio.sleep(delay)

            except httpx.TimeoutException as exc:
                self.logger.warning(
                    f"Timeout on attempt {attempts}: {exc}"
                )

                if attempts < max_attempts:
                    delay = self.retry_policy.get_backoff(attempts)

                    self.logger.warning(
                        f"Retrying in {delay:.2f}s"
                    )

                    await asyncio.sleep(delay)

            except httpx.RequestError as exc:
                self.logger.warning(
                    f"Network error on attempt {attempts}: "
                    f"{type(exc).__name__}: {exc}"
                )

                if attempts < max_attempts:
                    delay = self.retry_policy.get_backoff(attempts)

                    self.logger.warning(
                        f"Retrying in {delay:.2f}s"
                    )

                    await asyncio.sleep(delay)

        # Fallback
        if fallback_data is not None:
            self.logger.warning(
                "All attempts failed. Returning fallback data."
            )

            return {
                "status": "fallback",
                "response": fallback_data,
                "attempts": attempts,
                "retry_attempts": attempts - 1,
                "fallback_used": True,
                "error": "External API request failed after retries",
            }

        # Final failure
        self.logger.error(
            "All attempts failed. No fallback available."
        )

        return {
            "status": "error",
            "response": None,
            "attempts": attempts,
            "retry_attempts": attempts - 1,
            "fallback_used": False,
            "error": "External API request failed after retries",
        }