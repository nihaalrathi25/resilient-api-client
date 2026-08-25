from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_retries: int
    base_delay: float = 0.5
    max_delay: float = 10.0

    TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """
        Determines whether another attempt should be made.

        max_retries represents the number of retries AFTER
        the initial request.
        """
        return (
            status_code in self.TRANSIENT_STATUS_CODES
            and attempt <= self.max_retries
        )

    def get_backoff(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)