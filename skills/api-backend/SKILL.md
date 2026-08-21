---
name: api-backend
description: Backend API engineering — FastAPI/Python and Node/TypeScript services, REST + WebSocket design, robot/IoT telemetry ingestion, MQTT bridges, auth, databases. Use when building API servers, device/robot fleet backends, telemetry pipelines, or WebSocket services.
---

# Backend API Engineering

Production API standards for FastAPI (default) or NestJS/Express, with device-fleet patterns.

## Service design

- FastAPI: Pydantic v2 models for every request/response; routers per domain; dependency injection for DB/auth; `async def` end-to-end — never call blocking I/O (serial, heavy CPU) in the event loop; use `run_in_executor` or a worker.
- Versioned routes (`/api/v1/...`); consistent error envelope (RFC 9457 problem+json style); request IDs in logs.
- Config via environment (pydantic-settings) — never hardcode secrets; provide `.env.example`.

## REST rules

- Nouns for resources, correct verbs/status codes; pagination (cursor-based for feeds), filtering, and sorting on every list endpoint.
- Idempotency: PUT for full replace; idempotency keys for command endpoints that trigger physical actions (a retried "move arm" request must not execute twice).
- Validate at the edge; return 422 with field-level errors.

## Device / robot fleet patterns

- **Telemetry ingestion**: devices → MQTT (Mosquitto/EMQX) or WebSocket → backend bridge → store. Don't let devices write to the DB directly.
- Time-series storage: TimescaleDB or InfluxDB for telemetry; Postgres for entities (devices, users, missions). Downsample/retention policy from day one.
- **Command & control**: commands are records with lifecycle (`pending → sent → acked → done/failed/timeout`), not fire-and-forget HTTP. Timeout and reconciliation loop required.
- Device auth: per-device credentials/certs (mTLS or token), revocable; never a shared fleet secret.
- Offline tolerance: last-will messages (MQTT LWT) for presence; server marks devices stale after missed heartbeats.

## WebSocket endpoints

- Authenticate at upgrade; heartbeat ping/pong with idle timeout; broadcast via pub/sub (Redis) when scaled beyond one process.
- Define a small message schema (`{type, payload, ts}`) and validate it — don't pass raw strings around.

## Data & migrations

- SQLAlchemy 2.0 + Alembic (or Prisma in TS). Every schema change is a migration; no `create_all` in production.
- Transactions around multi-step writes; unique constraints in the DB, not just app checks.

## Quality bar

- Tests: pytest + httpx `AsyncClient` (or supertest); cover auth failures, validation errors, and the command-timeout path, not just 200s.
- Observability: structured logs (JSON), `/healthz` + `/readyz`, metrics (Prometheus) for queue depth, command latency, device online count.
