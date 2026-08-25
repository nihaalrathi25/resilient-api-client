# Resilient API Client

A production-oriented FastAPI service that makes external API calls resilient to **timeouts, rate limits, transient server errors, and temporary network failures** using retries, exponential backoff, structured logging, and optional fallback data.

---

## 🚀 Features

- ✅ Configurable request timeout
- ✅ Configurable retry count
- ✅ Exponential backoff
- ✅ Retries for transient HTTP errors
- ✅ Timeout and network error handling
- ✅ Optional fallback response
- ✅ Structured API responses
- ✅ Request validation with Pydantic
- ✅ Clear retry and failure logs
- ✅ Local flaky API simulator
- ✅ Interactive Swagger documentation
- ✅ OOP-based separation of responsibilities

---

## 🏗️ Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         │    Request      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    FastAPI      │
                         │   POST /request │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   ResilientAPIClient     │
                    │                          │
                    │ • Timeout handling       │
                    │ • Retry handling         │
                    │ • Backoff                │
                    │ • Logging                │
                    │ • Fallback               │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
             ┌──────────────┐          ┌──────────────┐
             │ RetryPolicy  │          │    HTTPX     │
             │              │          │    Client    │
             └──────────────┘          └───────┬──────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │ External API /  │
                                      │ Flaky Simulator │
                                      └────────┬────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              │                                 │
                              ▼                                 ▼
                       ┌─────────────┐                    ┌─────────────┐
                       │  Success    │                    │  Transient  │
                       │             │                    │   Failure   │
                       └─────────────┘                    └──────┬──────┘
                                                                 │
                                                                 ▼
                                                          Retry + Backoff
                                                                 │
                                                                 ▼
                                                        Attempts Exhausted
                                                                 │
                                                    ┌────────────┴───────────┐
                                                    │                        │
                                                    ▼                        ▼
                                             Fallback Data                Error
