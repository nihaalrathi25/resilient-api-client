# AI Prompts Used During Development

This file documents the AI-assisted prompts and development iterations used while implementing the Resilient API Client.

## Prompt 1 — Understand the Requirement

> Analyze the API timeout challenge and identify the minimum viable product required for functional correctness. Focus on timeout handling, transient errors, retry logic, exponential backoff, fallback behavior, logging, and reproducible failure scenarios.

### Result

The implementation was scoped around a small FastAPI application with:

* A resilient HTTP client
* Retry policy
* Exponential backoff
* Timeout handling
* Fallback responses
* Failure simulation
* Structured API responses

---

## Prompt 2 — Design the Architecture

> Design a clean Python OOP architecture for a resilient API client. Separate HTTP communication, retry decisions, request validation, fallback handling, logging, and API routing. Keep the implementation small enough for a 120-minute coding assessment.

### Result

The project was separated into:

* `ResilientAPIClient`
* `RetryPolicy`
* Pydantic request/response models
* API routes
* Flaky API simulator
* Logging utility

The main goal was separation of concerns without unnecessary infrastructure.

---

## Prompt 3 — Implement Retry Behavior

> Implement a retry policy for transient HTTP errors including 429, 500, 502, 503, and 504. Use exponential backoff and stop after the configured retry count.

### Result

A dedicated `RetryPolicy` class was created.

The policy distinguishes between transient and non-transient errors and calculates backoff delays independently from the HTTP client.

---

## Prompt 4 — Handle External API Failures

> Implement a resilient HTTP client that handles successful responses, HTTP failures, timeouts, network errors, retry attempts, exponential backoff, and optional fallback data. Return structured results instead of allowing external API failures to crash the service.

### Result

`ResilientAPIClient` was implemented with:

* HTTP status handling
* Timeout handling
* Network error handling
* Retry behavior
* Backoff
* Logging
* Fallback behavior
* Structured responses

---

## Prompt 5 — Reproduce Flaky Behavior

> Create a local FastAPI endpoint that can intentionally return configurable transient HTTP failures for a configurable number of requests before returning success. This should allow the retry mechanism to be demonstrated deterministically without depending on a third-party API.

### Result

A local `/flaky` simulator was added.

Example:

```text
/flaky?failures=3&failure_type=503
```

This allows the evaluator to reproduce:

```text
503
503
503
200
```

---

## Prompt 6 — Debug Successful API Responses

During testing, the client initially attempted to parse every successful response using `response.json()`.

Testing against an endpoint returning HTTP 200 with an empty body exposed an internal server error.

The implementation was revised to safely handle both JSON and text/empty responses.

### Improvement

The client now attempts JSON parsing and falls back to response text when the body is not valid JSON.

---

## Prompt 7 — Debug Retry Count

During testing, a configuration of:

```text
retry_count = 3
```

incorrectly resulted in only three total attempts instead of four.

The retry condition was reviewed and corrected.

The final interpretation is:

```text
1 initial request + 3 retries = 4 maximum attempts
```

This was verified using the local failure simulator.

---

## Prompt 8 — Improve Observability

> Add clear application logging showing request attempts, HTTP status codes, retry decisions, backoff duration, timeout/network errors, final success, and fallback usage.

### Result

A reusable logging utility was introduced.

Example output:

```text
INFO | Attempt 1/4
INFO | Received HTTP 503
WARNING | Transient HTTP 503. Retrying in 0.50s
INFO | Attempt 2/4
INFO | Received HTTP 503
WARNING | Transient HTTP 503. Retrying in 1.00s
INFO | Attempt 4/4
INFO | Received HTTP 200
INFO | Request successful
```

---

## Prompt 9 — Documentation Review

> Review the project from the perspective of an evaluator grading functional correctness, OOP, architecture, error handling, documentation, and AI prompting. Identify missing documentation and explain trade-offs and future production improvements.

### Result

The README was structured around:

* Overview
* Architecture
* Project structure
* Retry strategy
* Error handling
* Fallback behavior
* Setup
* Reproduction steps
* Logging
* Testing
* Design decisions
* Trade-offs
* Future improvements

---

## Development Approach

AI assistance was used primarily for:

1. Architecture brainstorming
2. Initial implementation suggestions
3. Debugging
4. Edge-case identification
5. Documentation review

The implementation was tested locally and iteratively corrected when actual runtime behavior differed from the expected behavior.

The most important iterations were:

```text
Initial retry implementation
        ↓
Successful empty response caused parsing failure
        ↓
Response parsing made resilient
        ↓
Retry count exposed an off-by-one error
        ↓
Retry policy corrected
        ↓
Failure simulator verified the complete flow
        ↓
Logging added for observability
```

## Final Principle

The implementation prioritizes understanding and verification over blindly accepting generated code. Runtime failures were used to identify and correct weaknesses in the initial implementation.
