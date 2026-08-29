# ADR-001 — Modular Monolith for v0.1

**Status:** Accepted

## Context
Five logical agents exist, but the initial product is operated by one developer and does not need independent scaling/deployment boundaries.

## Decision
Implement one backend codebase with bounded modules and asynchronous workers. Do not create five microservices.

## Consequences
Lower operational complexity, easier local development and tracing. Logical boundaries remain extractable if real scaling/ownership pressure appears.
