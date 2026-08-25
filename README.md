# Resilient API Client

## Overview

Resilient API Client is a Python-based service designed to handle intermittent failures when communicating with external APIs.

The client provides:

* Configurable request timeout
* Configurable retry count
* Retry handling for transient HTTP errors
* Exponential backoff between retries
* Timeout and network error handling
* Structured success, fallback, and error responses
* Optional fallback data
* Clear application logs
* A local flaky API simulator for reproducible failure scenarios
* Input validation using Pydantic

The project was designed specifically to demonstrate how an API client can remain reliable when external services experience temporary failures.

---

## Problem Statement

External APIs can fail intermittently because of:

* HTTP 429 rate limiting
* HTTP 500 internal server errors
* HTTP 502 bad gateway errors
* HTTP 503 service unavailable errors
* HTTP 504 gateway timeout errors
* Network failures
* Request timeouts

Immediately failing when one of these errors occurs can make an application unreliable.

This project solves the problem by retrying transient failures using exponential backoff and returning fallback data when all retry attempts are exhausted.

---

## Architecture

```text
                     Client Request
                           |
                           v
                    FastAPI /request
                           |
                           v
                  ResilientAPIClient
                           |
                    +------+------+
                    |             |
                    v             v
              RetryPolicy     HTTPX Client
                    |             |
                    |             v
                    |       External API
                    |             |
                    +------<------+
                           |
              +------------+------------+
              |                         |
              v                         v
          Successful                 Failure
           Response                    |
                                       v
                                Retry + Backoff
                                       |
                              Attempts exhausted
                                       |
                             +---------+---------+
                             |                   |
                             v                   v
                       Fallback Data          Error
```

### Main Components

#### `ResilientAPIClient`

Responsible for executing HTTP requests and coordinating:

* Timeout handling
* HTTP error handling
* Retry attempts
* Backoff
* Logging
* Fallback behavior

#### `RetryPolicy`

Encapsulates retry decisions.

Transient HTTP status codes:

```text
429
500
502
503
504
```

Non-transient errors such as `400` and `404` are not retried.

The retry policy also calculates exponential backoff.

#### `APIRequest`

Pydantic model responsible for validating:

* API URL
* Request payload
* Timeout
* Retry count
* Optional fallback data

#### `Flaky API Simulator`

The local simulator allows failures to be reproduced without depending on an unreliable third-party service.

It can simulate:

* HTTP 429
* HTTP 500
* HTTP 503
* Other configured failure responses
* Artificial delays for timeout testing

---

## Retry Strategy

The client treats transient failures differently from permanent failures.

For example, with:

```text
retry_count = 3
```

the client performs a maximum of four requests:

```text
Attempt 1 → Initial request
Attempt 2 → Retry 1
Attempt 3 → Retry 2
Attempt 4 → Retry 3
```

Backoff uses exponential growth:

```text
Retry 1 → 0.5 seconds
Retry 2 → 1.0 seconds
Retry 3 → 2.0 seconds
```

The delay is capped at a maximum value to prevent excessive waiting.

---

## Fallback Behavior

If all retry attempts fail and fallback data is provided, the client returns the fallback instead of crashing.

Example:

```json
{
  "status": "fallback",
  "response": {
    "message": "cached fallback"
  },
  "attempts": 4,
  "retry_attempts": 3,
  "fallback_used": true
}
```

If no fallback data is available, the client returns a structured error response.

---

## Project Structure

```text
resilient-api-client/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   └── resilient_client.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── retry_policy.py
│   │
│   ├── simulator/
│   │   ├── __init__.py
│   │   └── flaky_api.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py
│
├── tests/
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── prompt.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd resilient-api-client
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Health Check

```text
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Resilient Request

```text
POST /request
```

Example request:

```json
{
  "url": "http://127.0.0.1:8000/flaky?failures=3&failure_type=503",
  "payload": {
    "message": "test"
  },
  "timeout": 5,
  "retry_count": 3,
  "fallback_data": {
    "message": "cached fallback"
  }
}
```

### Flaky API Simulator

```text
POST /flaky
```

Example:

```text
/flaky?failures=3&failure_type=503
```

This simulates three failures followed by a successful response.

---

## Reproducing the Failure Scenario

Start the server:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Execute `/request` with:

```json
{
  "url": "http://127.0.0.1:8000/flaky?failures=3&failure_type=503",
  "payload": {
    "message": "test"
  },
  "timeout": 5,
  "retry_count": 3,
  "fallback_data": {
    "message": "cached fallback"
  }
}
```

The client will demonstrate:

```text
Attempt 1 → HTTP 503
Retry after 0.5 seconds

Attempt 2 → HTTP 503
Retry after 1.0 seconds

Attempt 3 → HTTP 503
Retry after 2.0 seconds

Attempt 4 → HTTP 200
Success
```

The terminal logs expose the complete retry process.

---

## Error Handling

The client handles:

### Transient HTTP failures

```text
429
500
502
503
504
```

These are retried with exponential backoff.

### Timeout failures

HTTPX timeout exceptions are caught and retried.

### Network failures

HTTPX request errors are caught and retried.

### Non-transient HTTP failures

Errors such as:

```text
400
401
403
404
```

are not retried because repeated requests are unlikely to resolve the underlying problem.

### Final failure

After all attempts are exhausted:

1. Fallback data is returned if available.
2. Otherwise a structured error response is returned.

---

## Logging

The client produces logs containing:

* Attempt number
* Maximum attempts
* Target URL
* HTTP status
* Error type
* Retry decision
* Backoff duration
* Final success/failure
* Fallback usage

Example:

```text
INFO | Attempt 1/4
INFO | Received HTTP 503
WARNING | Transient HTTP 503. Retrying in 0.50s
INFO | Attempt 2/4
INFO | Received HTTP 503
WARNING | Transient HTTP 503. Retrying in 1.00s
INFO | Attempt 3/4
INFO | Received HTTP 503
WARNING | Transient HTTP 503. Retrying in 2.00s
INFO | Attempt 4/4
INFO | Received HTTP 200
INFO | Request successful on attempt 4
```

---

## Testing

Run:

```bash
pytest -v
```

The important behaviors to test are:

* Transient errors are retried
* Non-transient errors are not retried
* Backoff increases exponentially
* Successful requests return immediately
* Retry attempts are counted correctly
* Fallback data is returned after exhausted retries

---

## Design Decisions

### Why FastAPI?

FastAPI provides simple API development, automatic request validation, and interactive OpenAPI documentation.

### Why HTTPX?

HTTPX provides asynchronous HTTP support and explicit timeout and network exception handling.

### Why a separate RetryPolicy?

Retry decisions are isolated from HTTP communication. This follows separation of concerns and makes the retry behavior easier to test and modify.

### Why exponential backoff?

Immediately retrying failed requests can increase load on an already struggling service. Exponential backoff spaces retries out and reduces unnecessary pressure on the external service.

### Why a local failure simulator?

A real external service cannot reliably reproduce the same failure sequence during evaluation. The simulator makes failure scenarios deterministic and easy to demonstrate.

---

## Trade-offs

The implementation intentionally focuses on the requirements of the assessment.

The current version uses:

* In-memory fallback data
* A local failure simulator
* Synchronous retry sequencing around asynchronous HTTP calls
* Simple exponential backoff

More advanced production capabilities were intentionally not added because they were outside the core requirements and assessment time constraints.

---

## Future Improvements

For a production system, the following could be added:

* Jitter to reduce synchronized retries
* Circuit breaker pattern
* Distributed caching
* Metrics using Prometheus
* Distributed tracing
* Structured JSON logging
* Configurable retry policies
* Authentication and secure API credentials
* Persistent fallback/cache storage
* Dependency injection for the HTTP transport
* More comprehensive integration and load tests

---

## Security

API credentials should never be hardcoded.

Environment-specific secrets should be stored in environment variables and excluded from Git using `.gitignore`.

---

## AI Prompting

The prompts and iterations used during development are documented in `prompt.md`.

---

## Summary

This project demonstrates a resilient API client that can:

```text
Detect transient failures
        ↓
Retry safely
        ↓
Apply exponential backoff
        ↓
Handle timeouts/network failures
        ↓
Return successful responses
        OR
Return fallback data
        OR
Return a structured error
```

The implementation prioritizes functional correctness, object-oriented separation of responsibilities, reproducibility, observability, and clear documentation.
